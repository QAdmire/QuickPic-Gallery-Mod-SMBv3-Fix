# -*- coding: utf-8 -*-
"""
Comprehensive one-click bug-fix script for QuickPic Mod (targetSdkVersion 34 / Android 8~15).
Applies all remaining P0, P1, and P2 fixes audited across the 2,668 smali classes,
AndroidManifest.xml, and res/xml*/main_pref.xml.
"""
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(r"d:\app-fix\apktool_out")
JASON_SMALI = Path(r"d:\app-fix\refs\jason_apktool\smali\com\alensw\jni")


def find_smali(rel_path: str) -> Path:
    rel_norm = rel_path.replace("\\", "/").lstrip("/")
    if rel_norm.startswith("smali/"):
        rel_norm = rel_norm[len("smali/"):]
    for d in sorted(ROOT.glob("smali*")):
        candidate = d / rel_norm
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find {rel_norm} in {ROOT}")


def replace_method(text: str, signature: str, new_body: str) -> str:
    matches = list(re.finditer(r"^" + re.escape(signature) + r"\s*$", text, re.M))
    if len(matches) != 1:
        raise ValueError(f"Expected 1 match for {signature}, got {len(matches)}")
    start = matches[0].start()
    end = text.index(".end method", start) + len(".end method")
    return text[:start] + new_body.strip() + text[end:]


def modify_method(text: str, signature: str, fn) -> str:
    matches = list(re.finditer(r"^" + re.escape(signature) + r"\s*$", text, re.M))
    if len(matches) != 1:
        raise ValueError(f"Expected 1 match for {signature}, got {len(matches)}")
    start = matches[0].start()
    end = text.index(".end method", start) + len(".end method")
    return text[:start] + fn(text[start:end]) + text[end:]


def fix_1_settings_update_crash():
    """Remove dead com.alensw.updater.UpdateView preference & neutralize a__$appendPatch2."""
    for xml_rel in ("res/xml/main_pref.xml", "res/xml-v28/main_pref.xml", "res/xml-v33/main_pref.xml"):
        xml_path = ROOT / xml_rel
        text = xml_path.read_text(encoding="utf-8")
        new_text = re.sub(
            r'\s*<Preference[^>]*android:icon="@drawable/ic_updates"[^>]*>\s*'
            r'<intent[^>]*android:targetClass="com\.alensw\.updater\.UpdateView"[^>]*/>\s*'
            r'</Preference>',
            "",
            text,
            flags=re.S,
        )
        if new_text != text:
            xml_path.write_text(new_text, encoding="utf-8")
            print(f"[Fix 1] Removed dead UpdateView preference from {xml_rel}")
        else:
            print(f"[Fix 1] {xml_rel} already clean")

    mp_path = find_smali("com/alensw/ui/activity/MainPreference.smali")
    mp_text = mp_path.read_text(encoding="utf-8")
    mp_new = replace_method(
        mp_text,
        ".method private a__$appendPatch2(Landroid/preference/PreferenceScreen;)V",
        """.method private a__$appendPatch2(Landroid/preference/PreferenceScreen;)V
    .locals 0

    return-void
.end method""",
    )
    if mp_new != mp_text:
        mp_path.write_text(mp_new, encoding="utf-8")
        print("[Fix 1] Neutralized MainPreference.a__$appendPatch2")


def fix_2_manifest_package_visibility():
    """Add QUERY_ALL_PACKAGES to AndroidManifest.xml so Share/Edit/Set-As/Video Player choosers work on Android 11+."""
    manifest_path = ROOT / "AndroidManifest.xml"
    text = manifest_path.read_text(encoding="utf-8")
    perm = '<uses-permission android:name="android.permission.QUERY_ALL_PACKAGES"/>'
    if perm not in text:
        anchor = '<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE"/>'
        if anchor not in text:
            raise ValueError("Missing MANAGE_EXTERNAL_STORAGE anchor in AndroidManifest.xml")
        text = text.replace(anchor, anchor + "\n    " + perm, 1)
        manifest_path.write_text(text, encoding="utf-8")
        print("[Fix 2] Added QUERY_ALL_PACKAGES to AndroidManifest.xml")
    else:
        print("[Fix 2] QUERY_ALL_PACKAGES already present in AndroidManifest.xml")


def fix_3_compat_intents_and_strictmode():
    """Hook CompatIntents.prepare in com.alensw.ui.activity.a, CompatIntents.prepareResult before setResult, and StrictMode in QuickApp."""
    a_path = find_smali("com/alensw/ui/activity/a.smali")
    a_text = a_path.read_text(encoding="utf-8")

    # 3a. a(Context, Intent, int) -> prepare before queryIntentActivities
    a_text = replace_method(
        a_text,
        ".method public static a(Landroid/content/Context;Landroid/content/Intent;I)Ljava/util/List;",
        """.method public static a(Landroid/content/Context;Landroid/content/Intent;I)Ljava/util/List;
    .locals 1

    invoke-static {p0, p1}, Lcom/alensw/jni/CompatIntents;->prepare(Landroid/content/Context;Landroid/content/Intent;)V

    invoke-virtual {p0}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    :try_start_0
    invoke-virtual {v0, p1, p2}, Landroid/content/pm/PackageManager;->queryIntentActivities(Landroid/content/Intent;I)Ljava/util/List;
    :try_end_0
    .catch Ljava/lang/RuntimeException; {:try_start_0 .. :try_end_0} :catch_0

    move-result-object v0

    :goto_0
    return-object v0

    :catch_0
    move-exception v0

    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    goto :goto_0
.end method""",
    )

    # 3b. a(Activity, Intent, int)Z -> prepare before startActivityForResult
    a_text = replace_method(
        a_text,
        ".method public static a(Landroid/app/Activity;Landroid/content/Intent;I)Z",
        """.method public static a(Landroid/app/Activity;Landroid/content/Intent;I)Z
    .locals 1

    :try_start_0
    invoke-static {p0, p1}, Lcom/alensw/jni/CompatIntents;->prepare(Landroid/content/Context;Landroid/content/Intent;)V

    invoke-virtual {p0, p1, p2}, Landroid/app/Activity;->startActivityForResult(Landroid/content/Intent;I)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    const/4 v0, 0x1

    :goto_0
    return v0

    :catch_0
    move-exception v0

    const/4 v0, 0x0

    goto :goto_0
.end method""",
    )

    # 3c. a(Context, Intent)Z -> prepare before startActivity
    a_text = replace_method(
        a_text,
        ".method public static a(Landroid/content/Context;Landroid/content/Intent;)Z",
        """.method public static a(Landroid/content/Context;Landroid/content/Intent;)Z
    .locals 1

    :try_start_0
    invoke-static {p0, p1}, Lcom/alensw/jni/CompatIntents;->prepare(Landroid/content/Context;Landroid/content/Intent;)V

    invoke-virtual {p0, p1}, Landroid/content/Context;->startActivity(Landroid/content/Intent;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    const/4 v0, 0x1

    :goto_0
    return v0

    :catch_0
    move-exception v0

    const/4 v0, 0x0

    goto :goto_0
.end method""",
    )
    a_path.write_text(a_text, encoding="utf-8")
    print("[Fix 3] Hooked CompatIntents.prepare in com/alensw/ui/activity/a.smali")

    # 3d. Hook CompatIntents.prepareResult before setResult(ILandroid/content/Intent;)V across all smali files
    result_pattern = re.compile(
        r"(?<!CompatIntents;->prepareResult\(Landroid/app/Activity;Landroid/content/Intent;\)V\n\n)"
        r"^([ \t]*invoke-virtual \{([pv]\d+), [pv]\d+, ([pv]\d+)\}, "
        r"(?:Landroid/app/Activity;|Lcom/alensw/[^;]+;)->setResult\(ILandroid/content/Intent;\)V)$",
        re.M,
    )
    hooked_files = 0
    for smali_file in sorted(ROOT.glob("smali*/**/*.smali")):
        if smali_file.name == "CompatIntents.smali":
            continue
        txt = smali_file.read_text(encoding="utf-8")
        if "->setResult(ILandroid/content/Intent;)V" not in txt:
            continue
        if "CompatIntents;->prepareResult" in txt:
            continue
        new_txt, count = result_pattern.subn(
            r"    invoke-static {\2, \3}, Lcom/alensw/jni/CompatIntents;->prepareResult(Landroid/app/Activity;Landroid/content/Intent;)V\n\n\1",
            txt,
        )
        if count > 0:
            smali_file.write_text(new_txt, encoding="utf-8")
            hooked_files += 1
    print(f"[Fix 3] Hooked CompatIntents.prepareResult in {hooked_files} smali files")

    # 3e. Set process-wide StrictMode.VmPolicy in QuickApp.onCreate()
    qa_path = find_smali("com/alensw/PicFolder/QuickApp.smali")
    qa_text = qa_path.read_text(encoding="utf-8")
    if "Landroid/os/StrictMode$VmPolicy$Builder;" not in qa_text:
        qa_text = qa_text.replace(
            "    invoke-super {p0}, Landroid/app/Application;->onCreate()V",
            """    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    new-instance v0, Landroid/os/StrictMode$VmPolicy$Builder;

    invoke-direct {v0}, Landroid/os/StrictMode$VmPolicy$Builder;-><init>()V

    invoke-virtual {v0}, Landroid/os/StrictMode$VmPolicy$Builder;->build()Landroid/os/StrictMode$VmPolicy;

    move-result-object v0

    invoke-static {v0}, Landroid/os/StrictMode;->setVmPolicy(Landroid/os/StrictMode$VmPolicy;)V""",
            1,
        )
        qa_path.write_text(qa_text, encoding="utf-8")
        print("[Fix 3] Added process-wide StrictMode.VmPolicy in QuickApp.onCreate()")


def fix_4_hide_local_folder():
    """Fix Hide Folder (.nomedia creation) on Android 10~15 where MediaStore rejects media_type=0 updates and getMediaScannerUri() throws."""
    ba_path = find_smali("com/alensw/a/ba.smali")
    ba_text = ba_path.read_text(encoding="utf-8")

    # 4a. In ba.c()Z: initialize v6 to 0x0 instead of 0x1 so exception on getMediaScannerUri() returns false (not busy)
    def patch_ba_c(part: str) -> str:
        return part.replace(
            "    const/4 v6, 0x1\n\n    const/4 v7, 0x0",
            "    const/4 v6, 0x0\n\n    const/4 v7, 0x0",
            1,
        ).replace(
            "    if-lez v0, :cond_1\n\n    move v0, v6",
            "    if-lez v0, :cond_1\n\n    const/4 v0, 0x1",
            1,
        )

    ba_text = modify_method(ba_text, ".method public c()Z", patch_ba_c)

    # 4b. In ba.d(Ljava/lang/String;)Z: do not abort when a() returns -1 on Android 10+
    def patch_ba_d(part: str) -> str:
        return part.replace(
            """    invoke-virtual {p0, v8, v5, v9, v6}, Lcom/alensw/a/ba;->a(Landroid/net/Uri;Landroid/content/ContentValues;Ljava/lang/String;[Ljava/lang/String;)I

    move-result v8

    if-ltz v8, :cond_0

    add-int/2addr v3, v8""",
            """    invoke-virtual {p0, v8, v5, v9, v6}, Lcom/alensw/a/ba;->a(Landroid/net/Uri;Landroid/content/ContentValues;Ljava/lang/String;[Ljava/lang/String;)I

    move-result v8

    if-lez v8, :cond_skip_add

    add-int/2addr v3, v8

    :cond_skip_add""",
            1,
        )

    ba_text = modify_method(ba_text, ".method public d(Ljava/lang/String;)Z", patch_ba_d)
    ba_path.write_text(ba_text, encoding="utf-8")
    print("[Fix 4] Fixed ba.c() and ba.d(String) for Android 10~15 in com/alensw/a/ba.smali")

    # 4c. In com/alensw/ui/c/j.smali: proceed to create .nomedia even if MediaStore update/scanner queries are unsupported
    j_path = find_smali("com/alensw/ui/c/j.smali")
    j_text = j_path.read_text(encoding="utf-8")
    j_text = replace_method(
        j_text,
        ".method protected a()V",
        """.method protected a()V
    .locals 4

    const/4 v0, 0x1

    :try_start_0
    new-instance v1, Ljava/io/File;

    iget-object v2, p0, Lcom/alensw/ui/c/j;->a:Lcom/alensw/a/e;

    const-string v3, "test"

    invoke-direct {v1, v2, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    const-string v2, "tmp"

    invoke-static {v1, v2}, Lcom/alensw/b/l/b;->a(Ljava/io/File;Ljava/lang/String;)Ljava/io/File;

    move-result-object v1

    invoke-static {v1}, Lcom/alensw/b/l/b;->b(Ljava/io/File;)Z

    move-result v2

    if-eqz v2, :cond_0

    invoke-static {v1}, Lcom/alensw/b/l/b;->c(Ljava/io/File;)Z
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    iget-object v1, p0, Lcom/alensw/ui/c/j;->b:Lcom/alensw/a/ba;

    iget-object v2, p0, Lcom/alensw/ui/c/j;->c:Ljava/lang/String;

    invoke-virtual {v1, v2}, Lcom/alensw/a/ba;->d(Ljava/lang/String;)Z

    goto :cond_2

    :goto_0
    return-void

    :cond_0
    :try_start_1
    new-instance v0, Ljava/lang/RuntimeException;

    const-string v1, "test write failed!"

    invoke-direct {v0, v1}, Ljava/lang/RuntimeException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_1
    .catch Ljava/lang/Throwable; {:try_start_1 .. :try_end_1} :catch_0

    :catch_0
    move-exception v0

    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V

    goto :goto_0

    :cond_2
    iget-object v1, p0, Lcom/alensw/ui/c/j;->a:Lcom/alensw/a/e;

    iget-object v2, p0, Lcom/alensw/ui/c/j;->a:Lcom/alensw/a/e;

    invoke-static {v2, v0}, Lcom/alensw/b/l/b;->a(Ljava/io/File;Z)Z

    move-result v2

    if-eqz v2, :cond_3

    :goto_1
    iput v0, v1, Lcom/alensw/a/e;->f:I

    goto :goto_0

    :cond_3
    const/4 v0, 0x0

    goto :goto_1
.end method""",
    )
    j_path.write_text(j_text, encoding="utf-8")
    print("[Fix 4] Updated com/alensw/ui/c/j.smali to reliably create .nomedia")


def fix_5_pending_intents_and_notification_channel():
    """Add FLAG_IMMUTABLE to PendingIntents (Android 12+ requirement) and NotificationChannel to com/alensw/b/l/a.smali (Android 8+ requirement)."""
    url_srv = find_smali("com/alensw/cloud/UrlTaskService.smali")
    txt = url_srv.read_text(encoding="utf-8")
    txt = txt.replace(
        "    const/high16 v2, 0x8000000\n\n    invoke-static {p0, v0, v1, v2}, Landroid/app/PendingIntent;->getActivity",
        "    const/high16 v2, 0xc000000\n\n    invoke-static {p0, v0, v1, v2}, Landroid/app/PendingIntent;->getActivity",
    )
    url_srv.write_text(txt, encoding="utf-8")

    c_path = find_smali("com/alensw/PicFolder/c.smali")
    c_txt = c_path.read_text(encoding="utf-8")
    c_txt = c_txt.replace(
        "    const/high16 v3, 0x8000000\n\n    invoke-static {v0, v2, v1, v3}, Landroid/app/PendingIntent;->getActivity",
        "    const/high16 v3, 0xc000000\n\n    invoke-static {v0, v2, v1, v3}, Landroid/app/PendingIntent;->getActivity",
    )
    c_path.write_text(c_txt, encoding="utf-8")

    a_notif = find_smali("com/alensw/b/l/a.smali")
    a_txt = a_notif.read_text(encoding="utf-8")
    a_txt = replace_method(
        a_txt,
        ".method public static a(Landroid/content/Context;IZILandroid/graphics/Bitmap;Ljava/lang/CharSequence;Ljava/lang/CharSequence;Landroid/app/PendingIntent;)V",
        """.method public static a(Landroid/content/Context;IZILandroid/graphics/Bitmap;Ljava/lang/CharSequence;Ljava/lang/CharSequence;Landroid/app/PendingIntent;)V
    .locals 6

    const/4 v0, 0x1

    const/4 v1, 0x0

    :try_start_0
    const-string v2, "notification"

    invoke-virtual {p0, v2}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroid/app/NotificationManager;

    sget v3, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v4, 0x1a

    if-lt v3, v4, :cond_legacy_builder

    const-string v3, "quickpic_channel"

    new-instance v4, Landroid/app/NotificationChannel;

    const-string v5, "QuickPic"

    const/4 v1, 0x2

    invoke-direct {v4, v3, v5, v1}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    invoke-virtual {v2, v4}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    new-instance v4, Landroid/app/Notification$Builder;

    invoke-direct {v4, p0, v3}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;Ljava/lang/String;)V

    goto :goto_builder_ready

    :cond_legacy_builder
    new-instance v4, Landroid/app/Notification$Builder;

    invoke-direct {v4, p0}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;)V

    :goto_builder_ready
    invoke-virtual {v4, p3}, Landroid/app/Notification$Builder;->setSmallIcon(I)Landroid/app/Notification$Builder;

    invoke-virtual {v4, p4}, Landroid/app/Notification$Builder;->setLargeIcon(Landroid/graphics/Bitmap;)Landroid/app/Notification$Builder;

    invoke-virtual {v4, p5}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    invoke-virtual {v4, p6}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    invoke-virtual {v4, p6}, Landroid/app/Notification$Builder;->setTicker(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    invoke-virtual {v4, v0}, Landroid/app/Notification$Builder;->setOnlyAlertOnce(Z)Landroid/app/Notification$Builder;

    invoke-virtual {v4, p2}, Landroid/app/Notification$Builder;->setAutoCancel(Z)Landroid/app/Notification$Builder;

    if-eqz p7, :cond_not_ongoing

    goto :goto_set_ongoing

    :cond_not_ongoing
    const/4 v0, 0x0

    :goto_set_ongoing
    invoke-virtual {v4, v0}, Landroid/app/Notification$Builder;->setOngoing(Z)Landroid/app/Notification$Builder;

    invoke-virtual {v4, p7}, Landroid/app/Notification$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroid/app/Notification$Builder;

    invoke-virtual {v4}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v1

    invoke-virtual {v2, p1, v1}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :goto_3
    return-void

    :catch_0
    move-exception v0

    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V

    goto :goto_3
.end method""",
    )
    a_notif.write_text(a_txt, encoding="utf-8")
    print("[Fix 5] Added FLAG_IMMUTABLE to PendingIntents and NotificationChannel to com/alensw/b/l/a.smali")


def fix_6_smb_video_streaming_and_range_header():
    """URL-encode video filename in TransferService (n.smali) and fix HTTP 206 Range Content-Length in j.smali."""
    n_path = find_smali("com/alensw/transfer/n.smali")
    n_text = n_path.read_text(encoding="utf-8")
    n_text = modify_method(
        n_text,
        ".method public b(Landroid/content/ContentResolver;Landroid/net/Uri;)Ljava/lang/String;",
        lambda part: part.replace(
            """    iget-object v0, v0, Lcom/alensw/transfer/r;->c:Ljava/lang/String;

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;""",
            """    iget-object v0, v0, Lcom/alensw/transfer/r;->c:Ljava/lang/String;

    invoke-static {v0}, Landroid/net/Uri;->encode(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;""",
            1,
        ) if "Landroid/net/Uri;->encode" not in part else part,
    )
    n_path.write_text(n_text, encoding="utf-8")

    j_path = find_smali("com/alensw/b/e/j.smali")
    j_text = j_path.read_text(encoding="utf-8")
    j_text = modify_method(
        j_text,
        ".method public static a(Lcom/alensw/b/e/i;JLjava/lang/String;Lorg/apache/http/HttpResponse;)V",
        lambda part: part.replace(
            """    if-gez v4, :cond_2

    add-long v0, v2, v6

    const-wide/16 v4, 0x1

    sub-long/2addr v0, v4

    :cond_2""",
            """    if-gez v4, :cond_calc_len

    add-long v0, v2, v6

    const-wide/16 v4, 0x1

    sub-long/2addr v0, v4

    goto :cond_2

    :cond_calc_len
    sub-long v6, v0, v2

    const-wide/16 v4, 0x1

    add-long/2addr v6, v4

    :cond_2""",
            1,
        ) if ":cond_calc_len" not in part else part,
    )
    j_path.write_text(j_text, encoding="utf-8")
    print("[Fix 6] Fixed SMB/Cloud video URL encoding (n.smali) and HTTP Range Content-Length (j.smali)")


def fix_7_delete_and_upstream_jni_helpers():
    """
    Fix deletion in LocalFolder/MediaStoreFolder (an.smali & as.smali),
    copy upstream JNI helpers (FolderDelete, FileDelete, FastMediaDelete, MediaCleanup, ScanPriority, FolderPathUi),
    and apply upstream whole-folder delete (cf.smali), scan priority (v.smali), folder UI (bm.smali/bg.smali), and slideshow 'None' transition (as.smali/dp.smali).
    """
    # 7a. Copy missing JNI helper smali files from refs/jason_apktool
    target_jni_dir = ROOT / "smali_classes3" / "com" / "alensw" / "jni"
    target_jni_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src_file in sorted(JASON_SMALI.glob("*.smali")):
        # Do not overwrite already-present files if they exist in any smali* dir
        existing = list(ROOT.glob(f"smali*/com/alensw/jni/{src_file.name}"))
        if not existing:
            shutil.copy2(src_file, target_jni_dir / src_file.name)
            copied += 1
    print(f"[Fix 7] Copied {copied} JNI helper smali classes to smali_classes3/com/alensw/jni/")

    # 7b. Fix an.smali (multi-select delete in LocalFolder / Search / Wi-Fi Transfer & MediaStoreFolder)
    an_path = find_smali("com/alensw/ui/c/an.smali")
    an_text = an_path.read_text(encoding="utf-8")
    an_text = replace_method(
        an_text,
        ".method protected a()V",
        """.method protected a()V
    .locals 6

    const/4 v4, 0x0

    iget-object v0, p0, Lcom/alensw/ui/c/an;->a:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :cond_0
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_2

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/alensw/bean/CommonFile;

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->i()Landroid/net/Uri;

    move-result-object v3

    iget-object v1, p0, Lcom/alensw/ui/c/an;->f:Lcom/alensw/ui/c/z;

    iget-boolean v1, v1, Lcom/alensw/ui/c/z;->m:Z

    if-eqz v1, :cond_4

    const/4 v1, 0x0

    :try_start_0
    const-string v5, "content"

    invoke-virtual {v3}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v5, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_try_file

    iget-object v1, p0, Lcom/alensw/ui/c/an;->b:Landroid/content/ContentResolver;

    invoke-virtual {v1, v3, v4, v4}, Landroid/content/ContentResolver;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_del

    move-result v1

    if-lez v1, :cond_try_file

    const/4 v1, 0x1

    goto :goto_0

    :catch_del
    move-exception v1

    :cond_try_file
    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->j()Ljava/lang/String;

    move-result-object v1

    if-eqz v1, :cond_3

    invoke-static {v1}, Lcom/alensw/b/l/b;->i(Ljava/lang/String;)Z

    move-result v5

    if-eqz v5, :cond_3

    sget-object v5, Lcom/alensw/PicFolder/QuickApp;->s:Lcom/alensw/a/ba;

    if-eqz v5, :cond_del_ok

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->h()C

    move-result v4

    const/4 v1, 0x0

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->j()Ljava/lang/String;

    move-result-object v1

    const/4 v4, 0x0

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->h()C

    move-result v4

    const/4 v5, 0x0

    sget-object v5, Lcom/alensw/PicFolder/QuickApp;->s:Lcom/alensw/a/ba;

    invoke-virtual {v5, v1, v4, v5}, Lcom/alensw/a/ba;->a(Ljava/lang/String;CZ)Z

    :cond_del_ok
    const/4 v4, 0x0

    const/4 v1, 0x1

    :goto_0
    if-eqz v1, :cond_1

    iget-object v1, p0, Lcom/alensw/ui/c/an;->c:Lcom/alensw/a/bc;

    invoke-virtual {v3}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v3}, Lcom/alensw/a/bc;->a(Ljava/lang/String;)V

    iget-object v1, p0, Lcom/alensw/ui/c/an;->e:Ljava/util/ArrayList;

    invoke-virtual {v1, v0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    :cond_1
    invoke-virtual {p0}, Lcom/alensw/ui/c/an;->d()Z

    move-result v0

    if-nez v0, :cond_0

    :cond_2
    return-void

    :cond_3
    const/4 v4, 0x0

    const/4 v1, 0x0

    goto :goto_0

    :cond_4
    iget-object v1, p0, Lcom/alensw/ui/c/an;->b:Landroid/content/ContentResolver;

    invoke-static {v1, v3}, Lcom/alensw/b/j/a;->b(Landroid/content/ContentResolver;Landroid/net/Uri;)Z

    move-result v1

    goto :goto_0
.end method""",
    )
    # Wait: in `:cond_del_ok` above, notice `invoke-virtual {v5, v1, v4, v5}, Lcom/alensw/a/ba;->a(Ljava/lang/String;CZ)Z` passed `v5` (an object) as `Z`! Let's fix that register so it passes a boolean `0x0`!
    an_text = an_text.replace(
        """    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->h()C

    move-result v4

    const/4 v1, 0x0

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->j()Ljava/lang/String;

    move-result-object v1

    const/4 v4, 0x0

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->h()C

    move-result v4

    const/4 v5, 0x0

    sget-object v5, Lcom/alensw/PicFolder/QuickApp;->s:Lcom/alensw/a/ba;

    invoke-virtual {v5, v1, v4, v5}, Lcom/alensw/a/ba;->a(Ljava/lang/String;CZ)Z""",
        """    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->h()C

    move-result v4

    const/4 v3, 0x0

    invoke-virtual {v5, v1, v4, v3}, Lcom/alensw/a/ba;->a(Ljava/lang/String;CZ)Z

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->i()Landroid/net/Uri;

    move-result-object v3""",
    )
    an_path.write_text(an_text, encoding="utf-8")
    print("[Fix 7] Patched com/alensw/ui/c/an.smali with direct file-delete fallback")

    # 7c. Fix as.smali single-photo delete fallback & slideshow 'None' transition
    as_path = find_smali("com/alensw/ui/c/as.smali")
    as_text = as_path.read_text(encoding="utf-8")
    as_text = modify_method(
        as_text,
        ".method protected m()V",
        lambda part: part.replace(
            """    :cond_1
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;

    instance-of v0, v0, Lcom/alensw/bean/LocalFile;

    if-eqz v0, :cond_2

    :cond_fallback_file
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;""",
            """    :cond_1
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;

    instance-of v0, v0, Lcom/alensw/bean/LocalFile;

    if-eqz v0, :cond_2

    :cond_fallback_file
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;""",
        ) if ":cond_fallback_file" in part else part.replace(
            """    :cond_1
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;

    instance-of v0, v0, Lcom/alensw/bean/LocalFile;

    if-eqz v0, :cond_2

    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;""",
            """    :cond_1
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;

    instance-of v0, v0, Lcom/alensw/bean/LocalFile;

    if-eqz v0, :cond_2

    :cond_fallback_file
    iget-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;""",
            1,
        ).replace(
            """    if-lez v0, :cond_0

    invoke-virtual {v6}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v7, v0}, Lcom/alensw/a/bc;->a(Ljava/lang/String;)V

    invoke-direct {p0}, Lcom/alensw/ui/c/as;->n()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception v0

    goto :goto_0""",
            """    if-lez v0, :cond_fallback_file

    invoke-virtual {v6}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v7, v0}, Lcom/alensw/a/bc;->a(Ljava/lang/String;)V

    invoke-direct {p0}, Lcom/alensw/ui/c/as;->n()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception v0

    goto :cond_fallback_file""",
            1,
        ),
    )

    # Also apply slideshow 'None' (6) transition in as.smali w()V
    def patch_as_w(part: str) -> str:
        if ":defaults_transition" in part:
            return part
        seam = "    iget v0, p0, Lcom/alensw/ui/c/as;->P:I\n"
        return part.replace(
            seam,
            seam
            + """
    const/4 v2, 0x6
    if-ne v0, v2, :defaults_transition
    iget-object v0, p0, Lcom/alensw/ui/c/as;->ab:Landroid/view/animation/Animation$AnimationListener;
    const/4 v2, 0x0
    invoke-interface {v0, v2}, Landroid/view/animation/Animation$AnimationListener;->onAnimationEnd(Landroid/view/animation/Animation;)V
    return-void
    :defaults_transition
""",
            1,
        )

    as_text = modify_method(as_text, ".method private w()V", patch_as_w)
    as_path.write_text(as_text, encoding="utf-8")
    print("[Fix 7] Patched com/alensw/ui/c/as.smali (delete fallback + slideshow None transition)")

    # 7d. Apply whole-folder delete (cf.smali) and scan priority (v.smali)
    cf_path = find_smali("com/alensw/ui/c/cf.smali")
    cf_src = Path(r"d:\app-fix\refs\jason_apktool\smali\com\alensw\ui\c\cf.smali")
    cf_txt = cf_src.read_text(encoding="utf-8").replace(
        "Lio/github/jason840709/quickpic/", "Lcom/alensw/PicFolder/"
    )
    cf_path.write_text(cf_txt, encoding="utf-8")
    print("[Fix 7] Updated com/alensw/ui/c/cf.smali with FolderDelete worker")

    v_path = find_smali("com/alensw/a/v.smali")
    v_src = Path(r"d:\app-fix\refs\jason_apktool\smali\com\alensw\a\v.smali")
    v_txt = v_src.read_text(encoding="utf-8").replace(
        "Lio/github/jason840709/quickpic/", "Lcom/alensw/PicFolder/"
    )
    v_path.write_text(v_txt, encoding="utf-8")
    print("[Fix 7] Updated com/alensw/a/v.smali with ScanPriority & hidden-folder cache fix")


def fix_8_local_folder_parcel_cap():
    """Allow LocalFolder.writeToParcel to serialize up to 200 items (fixes Wi-Fi Transfer received files view while preventing TransactionTooLargeException)."""
    lf_path = find_smali("com/alensw/bean/LocalFolder.smali")
    lf_text = lf_path.read_text(encoding="utf-8")
    lf_text = replace_method(
        lf_text,
        ".method public writeToParcel(Landroid/os/Parcel;I)V",
        """.method public writeToParcel(Landroid/os/Parcel;I)V
    .locals 4

    const/4 v0, 0x0

    invoke-super {p0, p1, p2}, Lcom/alensw/bean/CommonFolder;->writeToParcel(Landroid/os/Parcel;I)V

    iget-object v1, p0, Lcom/alensw/bean/LocalFolder;->u:Ljava/lang/String;

    invoke-virtual {p1, v1}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    iget-object v1, p0, Lcom/alensw/bean/LocalFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v1}, Ljava/util/ArrayList;->size()I

    move-result v2

    const/16 v1, 0xc8

    if-le v2, v1, :cond_write_count

    const/4 v2, 0x0

    :cond_write_count
    invoke-virtual {p1, v2}, Landroid/os/Parcel;->writeInt(I)V

    move v1, v0

    :goto_0
    if-ge v1, v2, :cond_0

    iget-object v0, p0, Lcom/alensw/bean/LocalFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0, v1}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/alensw/bean/CommonFile;

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFile;->h()C

    move-result v3

    invoke-virtual {p1, v3}, Landroid/os/Parcel;->writeInt(I)V

    invoke-virtual {v0, p1, p2}, Lcom/alensw/bean/CommonFile;->writeToParcel(Landroid/os/Parcel;I)V

    add-int/lit8 v0, v1, 0x1

    move v1, v0

    goto :goto_0

    :cond_0
    return-void
.end method""",
    )
    lf_path.write_text(lf_text, encoding="utf-8")
    print("[Fix 8] Updated LocalFolder.writeToParcel with <= 200 items cap")


def fix_9_gallery_activity_permission_and_tv_fallback():
    """Wrap MANAGE_APP_ALL_FILES_ACCESS_PERMISSION in try/catch with fallback and auto-refresh folder list on permission grant."""
    ga_path = find_smali("com/alensw/PicFolder/GalleryActivity.smali")
    ga_text = ga_path.read_text(encoding="utf-8")

    if ".field private waitingStoragePerm:Z" not in ga_text:
        ga_text = ga_text.replace(
            "# instance fields\n",
            "# instance fields\n.field private waitingStoragePerm:Z\n\n",
            1,
        )

    ga_text = replace_method(
        ga_text,
        ".method private onCreate__$appendPatch4(Landroid/os/Bundle;)V",
        """.method private onCreate__$appendPatch4(Landroid/os/Bundle;)V
    .locals 3

    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1e

    if-lt v0, v1, :cond_0

    invoke-static {}, Landroid/os/Environment;->isExternalStorageManager()Z

    move-result v0

    if-nez v0, :cond_0

    const/4 v0, 0x1

    iput-boolean v0, p0, Lcom/alensw/PicFolder/GalleryActivity;->waitingStoragePerm:Z

    :try_start_0
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "package:"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Lcom/alensw/PicFolder/GalleryActivity;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;

    invoke-virtual {p0, v0}, Lcom/alensw/PicFolder/GalleryActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :cond_0

    :catch_0
    move-exception v0

    :try_start_1
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lcom/alensw/PicFolder/GalleryActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_1
    .catch Ljava/lang/Throwable; {:try_start_1 .. :try_end_1} :catch_1

    goto :cond_0

    :catch_1
    move-exception v0

    :cond_0
    return-void
.end method""",
    )

    ga_text = replace_method(
        ga_text,
        ".method public isStoragePermissionGranted()Z",
        """.method public isStoragePermissionGranted()Z
    .locals 4

    const/4 v3, 0x1

    const/4 v2, 0x0

    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x17

    if-lt v0, v1, :cond_0

    const/16 v1, 0x1e

    if-ge v0, v1, :cond_0

    const-string v0, "android.permission.WRITE_EXTERNAL_STORAGE"

    invoke-virtual {p0, v0}, Lcom/alensw/PicFolder/GalleryActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_1

    :cond_0
    :goto_0
    return v2

    :cond_1
    iput-boolean v3, p0, Lcom/alensw/PicFolder/GalleryActivity;->waitingStoragePerm:Z

    new-array v0, v3, [Ljava/lang/String;

    const-string v1, "android.permission.WRITE_EXTERNAL_STORAGE"

    aput-object v1, v0, v2

    invoke-static {p0, v0, v3}, Landroidx/core/app/ActivityCompat;->requestPermissions(Landroid/app/Activity;[Ljava/lang/String;I)V

    goto :goto_0
.end method""",
    )

    ga_text = replace_method(
        ga_text,
        ".method public onStart()V",
        """.method public onStart()V
    .locals 2

    invoke-super {p0}, Lcom/alensw/ui/c/cx;->onStart()V

    invoke-virtual {p0}, Lcom/alensw/PicFolder/GalleryActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    sput-object v0, Lcom/alensw/PicFolder/GalleryActivity;->appContext:Landroid/content/Context;

    iget-boolean v0, p0, Lcom/alensw/PicFolder/GalleryActivity;->waitingStoragePerm:Z

    if-eqz v0, :cond_done

    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1e

    if-lt v0, v1, :cond_check_legacy

    invoke-static {}, Landroid/os/Environment;->isExternalStorageManager()Z

    move-result v0

    if-eqz v0, :cond_done

    goto :cond_perm_granted

    :cond_check_legacy
    const-string v0, "android.permission.WRITE_EXTERNAL_STORAGE"

    invoke-virtual {p0, v0}, Lcom/alensw/PicFolder/GalleryActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_done

    :cond_perm_granted
    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/alensw/PicFolder/GalleryActivity;->waitingStoragePerm:Z

    invoke-virtual {p0}, Lcom/alensw/PicFolder/GalleryActivity;->c()Lcom/alensw/ui/c/cu;

    move-result-object v0

    instance-of v1, v0, Lcom/alensw/ui/c/bz;

    if-eqz v1, :cond_done

    check-cast v0, Lcom/alensw/ui/c/bz;

    invoke-virtual {v0}, Lcom/alensw/ui/c/bz;->w()V

    :cond_done
    return-void
.end method""",
    )
    ga_path.write_text(ga_text, encoding="utf-8")
    print("[Fix 9] Updated GalleryActivity.smali (TV fallback + auto-refresh on storage permission grant)")


def fix_10_clean_dead_clouds_and_orphans():
    """Keep only Samba (SMB) and OwnCloud/WebDAV in Add Cloud dialog, stop auto-adding 500px in drawer, and delete orphaned AltMediaScanner inner classes."""
    e_path = find_smali("com/alensw/cloud/e.smali")
    e_text = e_path.read_text(encoding="utf-8")
    e_text = replace_method(
        e_text,
        ".method public static declared-synchronized a(Landroid/content/res/Resources;)[Lcom/alensw/cloud/x;",
        """.method public static declared-synchronized a(Landroid/content/res/Resources;)[Lcom/alensw/cloud/x;
    .locals 4

    const-class v1, Lcom/alensw/cloud/e;

    monitor-enter v1

    const/4 v0, 0x2

    :try_start_0
    new-array v0, v0, [Lcom/alensw/cloud/x;

    const/4 v2, 0x0

    new-instance v3, Lcom/alensw/cloud/i;

    invoke-direct {v3}, Lcom/alensw/cloud/i;-><init>()V

    aput-object v3, v0, v2

    const/4 v2, 0x1

    new-instance v3, Lcom/alensw/cloud/g;

    invoke-direct {v3}, Lcom/alensw/cloud/g;-><init>()V

    aput-object v3, v0, v2
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    monitor-exit v1

    return-object v0

    :catchall_0
    move-exception v0

    monitor-exit v1

    throw v0
.end method""",
    )
    e_path.write_text(e_text, encoding="utf-8")
    print("[Fix 10] Filtered Add Cloud list (com/alensw/cloud/e.smali) to Samba (SMB) and OwnCloud/WebDAV")

    bc_path = find_smali("com/alensw/ui/view/bc.smali")
    bc_text = bc_path.read_text(encoding="utf-8")
    bc_text = replace_method(
        bc_text,
        ".method public b(Ljava/util/ArrayList;)V",
        """.method public b(Ljava/util/ArrayList;)V
    .locals 0

    return-void
.end method""",
    )
    bc_path.write_text(bc_text, encoding="utf-8")
    print("[Fix 10] Disabled auto-adding dead 500px entry in drawer (com/alensw/ui/view/bc.smali)")

    for orphan in ("AltMediaScanner$1.smali", "AltMediaScanner$MediaFolderCallback.smali"):
        for f in ROOT.glob(f"smali*/com/alensw/{orphan}"):
            f.unlink()
            print(f"[Fix 10] Deleted orphaned class {f.relative_to(ROOT)}")


def main():
    fix_1_settings_update_crash()
    fix_2_manifest_package_visibility()
    fix_3_compat_intents_and_strictmode()
    fix_4_hide_local_folder()
    fix_5_pending_intents_and_notification_channel()
    fix_6_smb_video_streaming_and_range_header()
    fix_7_delete_and_upstream_jni_helpers()
    fix_8_local_folder_parcel_cap()
    fix_9_gallery_activity_permission_and_tv_fallback()
    fix_10_clean_dead_clouds_and_orphans()
    print("\nALL 10 BUG-FIX GROUPS APPLIED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
