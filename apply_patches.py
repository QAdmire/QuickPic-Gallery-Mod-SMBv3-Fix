# -*- coding: utf-8 -*-
import os
import re
import shutil
from pathlib import Path

APKTOOL_OUT = Path(r"d:\app-fix\apktool_out")
JASON_APKTOOL = Path(r"d:\app-fix\refs\jason_apktool")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, desc: str) -> str:
    # Normalize CRLF to LF for reliable matching
    norm_text = text.replace("\r\n", "\n")
    norm_old = old.replace("\r\n", "\n")
    norm_new = new.replace("\r\n", "\n")
    count = norm_text.count(norm_old)
    if count != 1:
        raise ValueError(f"[{desc}] Expected 1 occurrence, found {count}")
    return norm_text.replace(norm_old, norm_new, 1)


def step1_patch_smb_and_parcelables():
    print("=== Step 1: Patching SMB Folder State & Parcelable Serialization ===")

    # 1a. DocumentFolder.writeToParcel: do not serialize child list n into Binder Parcel
    doc_folder = APKTOOL_OUT / "smali/com/alensw/bean/DocumentFolder.smali"
    text = read_text(doc_folder)
    old_doc = """.method public writeToParcel(Landroid/os/Parcel;I)V
    .locals 2

    invoke-super {p0, p1, p2}, Lcom/alensw/bean/CommonFolder;->writeToParcel(Landroid/os/Parcel;I)V

    iget-object v0, p0, Lcom/alensw/bean/DocumentFolder;->u:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    iget-object v0, p0, Lcom/alensw/bean/DocumentFolder;->v:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    iget-object v0, p0, Lcom/alensw/bean/DocumentFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I

    move-result v0

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeInt(I)V

    iget-object v0, p0, Lcom/alensw/bean/DocumentFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v1

    :goto_0
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_0

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/alensw/bean/CommonFile;

    invoke-virtual {v0, p1, p2}, Lcom/alensw/bean/CommonFile;->writeToParcel(Landroid/os/Parcel;I)V

    goto :goto_0

    :cond_0
    return-void
.end method"""
    new_doc = """.method public writeToParcel(Landroid/os/Parcel;I)V
    .locals 2

    invoke-super {p0, p1, p2}, Lcom/alensw/bean/CommonFolder;->writeToParcel(Landroid/os/Parcel;I)V

    iget-object v0, p0, Lcom/alensw/bean/DocumentFolder;->u:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    iget-object v0, p0, Lcom/alensw/bean/DocumentFolder;->v:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    const/4 v0, 0x0

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeInt(I)V

    return-void
.end method"""
    if new_doc not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_doc, new_doc, "DocumentFolder.writeToParcel")
        write_text(doc_folder, text)
        print("  + Patched DocumentFolder.writeToParcel")

    # 1b. LocalFolder.writeToParcel
    local_folder = APKTOOL_OUT / "smali/com/alensw/bean/LocalFolder.smali"
    text = read_text(local_folder)
    old_local = """.method public writeToParcel(Landroid/os/Parcel;I)V
    .locals 2

    invoke-super {p0, p1, p2}, Lcom/alensw/bean/CommonFolder;->writeToParcel(Landroid/os/Parcel;I)V

    iget-object v0, p0, Lcom/alensw/bean/LocalFolder;->u:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    iget-object v0, p0, Lcom/alensw/bean/LocalFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I

    move-result v0

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeInt(I)V

    iget-object v0, p0, Lcom/alensw/bean/LocalFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v1

    :goto_0
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_0

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/alensw/bean/CommonFile;

    invoke-virtual {v0, p1, p2}, Lcom/alensw/bean/CommonFile;->writeToParcel(Landroid/os/Parcel;I)V

    goto :goto_0

    :cond_0
    return-void
.end method"""
    new_local = """.method public writeToParcel(Landroid/os/Parcel;I)V
    .locals 2

    invoke-super {p0, p1, p2}, Lcom/alensw/bean/CommonFolder;->writeToParcel(Landroid/os/Parcel;I)V

    iget-object v0, p0, Lcom/alensw/bean/LocalFolder;->u:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    const/4 v0, 0x0

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeInt(I)V

    return-void
.end method"""
    if new_local not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_local, new_local, "LocalFolder.writeToParcel")
        write_text(local_folder, text)
        print("  + Patched LocalFolder.writeToParcel")

    # 1c. MediaStoreFolder.writeToParcel
    ms_folder = APKTOOL_OUT / "smali/com/alensw/bean/MediaStoreFolder.smali"
    text = read_text(ms_folder)
    old_ms = """    iget-object v0, p0, Lcom/alensw/bean/MediaStoreFolder;->z:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    iget-object v0, p0, Lcom/alensw/bean/MediaStoreFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I

    move-result v0

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeInt(I)V

    iget-object v0, p0, Lcom/alensw/bean/MediaStoreFolder;->n:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v1

    :goto_2
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_2

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/alensw/bean/CommonFile;

    invoke-virtual {v0, p1, p2}, Lcom/alensw/bean/CommonFile;->writeToParcel(Landroid/os/Parcel;I)V

    goto :goto_2

    :cond_0
    move v0, v2

    goto :goto_0

    :cond_1
    move v1, v2

    goto :goto_1

    :cond_2
    return-void
.end method"""
    new_ms = """    iget-object v0, p0, Lcom/alensw/bean/MediaStoreFolder;->z:Ljava/lang/String;

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeString(Ljava/lang/String;)V

    const/4 v0, 0x0

    invoke-virtual {p1, v0}, Landroid/os/Parcel;->writeInt(I)V

    goto :goto_3

    :cond_0
    move v0, v2

    goto :goto_0

    :cond_1
    move v1, v2

    goto :goto_1

    :cond_2
    :goto_3
    return-void
.end method"""
    if new_ms not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_ms, new_ms, "MediaStoreFolder.writeToParcel")
        write_text(ms_folder, text)
        print("  + Patched MediaStoreFolder.writeToParcel")

    # 1d. z.smali:
    # - Clone folder without children in z.a(CommonFolder, boolean, String)
    # - Clone this.y in z.a(Bundle) and restore scroll_pos from Bundle into z.z
    # - Save scroll_pos in z.b(Bundle)
    z_smali = APKTOOL_OUT / "smali/com/alensw/ui/c/z.smali"
    text = read_text(z_smali)

    old_z_intent = """.method public static a(Lcom/alensw/bean/CommonFolder;ZLjava/lang/String;)Landroid/content/Intent;
    .locals 2

    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    invoke-virtual {p0}, Lcom/alensw/bean/CommonFolder;->i()Landroid/net/Uri;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;

    const-string v1, "QuickPic.folder"

    invoke-virtual {v0, v1, p0}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Landroid/os/Parcelable;)Landroid/content/Intent;"""

    new_z_intent = """.method public static a(Lcom/alensw/bean/CommonFolder;ZLjava/lang/String;)Landroid/content/Intent;
    .locals 2

    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    invoke-virtual {p0}, Lcom/alensw/bean/CommonFolder;->i()Landroid/net/Uri;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;

    const/4 v1, 0x0

    invoke-virtual {p0, v1}, Lcom/alensw/bean/CommonFolder;->a(Z)Lcom/alensw/bean/CommonFolder;

    move-result-object p0

    const-string v1, "QuickPic.folder"

    invoke-virtual {v0, v1, p0}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Landroid/os/Parcelable;)Landroid/content/Intent;"""

    if new_z_intent not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_z_intent, new_z_intent, "z.a(CommonFolder,Z,String)")

    old_z_create = """    iget-object v0, p0, Lcom/alensw/ui/c/z;->y:Lcom/alensw/bean/CommonFolder;

    if-nez v0, :cond_0

    invoke-virtual {p0}, Lcom/alensw/ui/c/z;->E()V

    :goto_0
    return-void

    :cond_0
    sget-object v0, Lcom/alensw/PicFolder/QuickApp;->w:Lcom/alensw/b/a/a;"""

    new_z_create = """    iget-object v0, p0, Lcom/alensw/ui/c/z;->y:Lcom/alensw/bean/CommonFolder;

    if-nez v0, :cond_0

    invoke-virtual {p0}, Lcom/alensw/ui/c/z;->E()V

    :goto_0
    return-void

    :cond_0
    invoke-virtual {v0, v2}, Lcom/alensw/bean/CommonFolder;->a(Z)Lcom/alensw/bean/CommonFolder;

    move-result-object v0

    iput-object v0, p0, Lcom/alensw/ui/c/z;->y:Lcom/alensw/bean/CommonFolder;

    if-eqz p1, :cond_restore_done

    const-string v0, "scroll_pos"

    invoke-virtual {p1, v0}, Landroid/os/Bundle;->containsKey(Ljava/lang/String;)Z

    move-result v3

    if-eqz v3, :cond_restore_done

    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getFloat(Ljava/lang/String;)F

    move-result v0

    invoke-static {v0}, Ljava/lang/Float;->valueOf(F)Ljava/lang/Float;

    move-result-object v0

    sget-object v3, Lcom/alensw/ui/c/z;->z:Ljava/util/HashMap;

    iget-object p1, p0, Lcom/alensw/ui/c/z;->y:Lcom/alensw/bean/CommonFolder;

    invoke-virtual {p1}, Lcom/alensw/bean/CommonFolder;->i()Landroid/net/Uri;

    move-result-object p1

    invoke-virtual {v3, p1, v0}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    :cond_restore_done
    sget-object v0, Lcom/alensw/PicFolder/QuickApp;->w:Lcom/alensw/b/a/a;"""

    if new_z_create not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_z_create, new_z_create, "z.a(Bundle)")

    old_z_save = """.method public b(Landroid/os/Bundle;)V
    .locals 0

    return-void
.end method"""

    new_z_save = """.method public b(Landroid/os/Bundle;)V
    .locals 2

    iget-object v0, p0, Lcom/alensw/ui/c/z;->f:Lcom/alensw/ui/view/ImageGridView;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lcom/alensw/ui/view/ImageGridView;->getScrollPos()F

    move-result v0

    const-string v1, "scroll_pos"

    invoke-virtual {p1, v1, v0}, Landroid/os/Bundle;->putFloat(Ljava/lang/String;F)V

    :cond_0
    return-void
.end method"""

    if new_z_save not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_z_save, new_z_save, "z.b(Bundle)")

    write_text(z_smali, text)
    print("  + Patched z.smali (intent folder clone, this.y decouple, scroll_pos save/restore)")

    # 1e. as.smali: fallback to Intent data URI when restored CommonFolder has empty file list
    as_smali = APKTOOL_OUT / "smali_classes4/com/alensw/ui/c/as.smali"
    text = read_text(as_smali)
    old_as = """    :cond_1
    iget-object v0, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    if-eqz v0, :cond_2

    iget-object v0, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    iget-object v5, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    iget v5, v5, Lcom/alensw/bean/CommonFolder;->k:I

    invoke-virtual {v0, v5}, Lcom/alensw/bean/CommonFolder;->a(I)Lcom/alensw/bean/CommonFile;

    move-result-object v0

    iput-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;

    :cond_2"""

    new_as = """    :cond_1
    iget-object v0, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    if-eqz v0, :cond_2

    invoke-virtual {v0}, Lcom/alensw/bean/CommonFolder;->n()Z

    move-result v0

    if-eqz v0, :cond_folder_not_empty

    iput-object v2, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    goto :cond_2

    :cond_folder_not_empty
    iget-object v0, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    iget-object v5, p0, Lcom/alensw/ui/c/as;->k:Lcom/alensw/bean/CommonFolder;

    iget v5, v5, Lcom/alensw/bean/CommonFolder;->k:I

    invoke-virtual {v0, v5}, Lcom/alensw/bean/CommonFolder;->a(I)Lcom/alensw/bean/CommonFile;

    move-result-object v0

    iput-object v0, p0, Lcom/alensw/ui/c/as;->l:Lcom/alensw/bean/CommonFile;

    :cond_2"""

    if new_as not in text.replace("\r\n", "\n"):
        text = replace_once(text, old_as, new_as, "as.a(Bundle) empty folder fallback")
        write_text(as_smali, text)
        print("  + Patched as.smali (empty folder fallback to Intent data URI)")


def step2_port_pure_java_jni_engine():
    print("=== Step 2: Porting jason840709 Pure-Java 64-Bit JniUtils Engine ===")
    src_jni = JASON_APKTOOL / "smali/com/alensw/jni"
    dst_jni = APKTOOL_OUT / "smali_classes3/com/alensw/jni"
    dst_jni.mkdir(parents=True, exist_ok=True)

    core_prefixes = (
        "JniUtils",
        "QuickPicExif",
        "WebPAnimation",
        "MediaDates",
        "CompatIntents",
        "AnimationFormats",
        "AnimationPlayback",
    )
    copied = []
    for f in sorted(src_jni.glob("*.smali")):
        if f.name.startswith(core_prefixes):
            shutil.copy2(f, dst_jni / f.name)
            copied.append(f.name)
    print(f"  + Copied {len(copied)} pure-Java JNI classes into smali_classes3/com/alensw/jni/")

    # Add static init(Ljava/lang/String;)I stub to JniUtils.smali for safety
    jni_utils = dst_jni / "JniUtils.smali"
    text = read_text(jni_utils).replace("\r\n", "\n")
    init_stub = """
.method public static init(Ljava/lang/String;)I
    .locals 1

    const/4 v0, 0x0

    return v0
.end method
"""
    if ".method public static init(Ljava/lang/String;)I" not in text:
        text = text.rstrip() + "\n" + init_stub
        write_text(jni_utils, text)
        print("  + Added JniUtils.init(String)I compatibility stub")

    # Replace broken Java scanner rewrite in al.smali with clean original al.smali calling JniUtils.fsScanPictures
    src_al = JASON_APKTOOL / "smali/com/alensw/a/al.smali"
    dst_al = APKTOOL_OUT / "smali_classes3/com/alensw/a/al.smali"
    shutil.copy2(src_al, dst_al)
    print("  + Restored clean com/alensw/a/al.smali (delegating to pure-Java JniUtils.fsScanPictures)")

    # Remove dead community mod classes AltMediaScanner.smali & Utils.smali
    for dead in ("AltMediaScanner.smali", "Utils.smali"):
        dead_path = APKTOOL_OUT / "smali_classes2/com/alensw" / dead
        if dead_path.exists():
            dead_path.unlink()
            print(f"  + Removed dead community mod class: {dead}")

    # Remove lib/ directory (broken 64-bit stub libqpicjni156.so and 32-bit .so files)
    lib_dir = APKTOOL_OUT / "lib"
    if lib_dir.exists():
        shutil.rmtree(lib_dir)
        print("  + Removed native lib/ folder (pure-Java JniUtils engine is now 100% 32/64-bit architecture independent)")

    # Hook QuickPicExif.setCacheDirectory(getCacheDir()) in QuickApp.onCreate()
    quick_app = APKTOOL_OUT / "smali_classes4/com/alensw/PicFolder/QuickApp.smali"
    text = read_text(quick_app)
    old_qa = """    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    sput-object p0, Lcom/alensw/PicFolder/QuickApp;->B:Lcom/alensw/PicFolder/QuickApp;"""
    new_qa = """    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    invoke-virtual {p0}, Landroid/content/Context;->getCacheDir()Ljava/io/File;

    move-result-object v0

    invoke-static {v0}, Lcom/alensw/jni/QuickPicExif;->setCacheDirectory(Ljava/io/File;)V

    sput-object p0, Lcom/alensw/PicFolder/QuickApp;->B:Lcom/alensw/PicFolder/QuickApp;"""
    if "QuickPicExif;->setCacheDirectory" not in text:
        text = replace_once(text, old_qa, new_qa, "QuickApp.onCreate setCacheDirectory")
        write_text(quick_app, text)
        print("  + Hooked QuickPicExif.setCacheDirectory in QuickApp.onCreate()")

    # Apply animated WebP / GIF support patches (adapted for multidex locations in apktool_out)
    HELPER = "Lcom/alensw/jni/AnimationFormats;"
    CLOCK = "Lcom/alensw/jni/AnimationPlayback;"

    def body_span(t, sig):
        s = t.index(sig)
        e = t.index(".end method", s) + len(".end method")
        return s, e, t[s:e]

    at_path = APKTOOL_OUT / "smali_classes3/com/alensw/a/at.smali"
    at_text = read_text(at_path).replace("\r\n", "\n")
    for name in ("a", "b", "c"):
        sig = f".method private {name}(Lcom/alensw/b/c/f;Landroid/net/Uri;)Lcom/alensw/b/h/j;"
        s, e, part = body_span(at_text, sig)
        if HELPER + "->isCandidate" not in part:
            pattern = (
                r'(    const-string (v\d+), "image/gif"\s+)'
                r'(    iget-object (v\d+), v\d+, Lcom/alensw/b/h/a;->outMimeType:Ljava/lang/String;\s+)'
                r'    invoke-virtual \{\2, \4\}, Ljava/lang/String;->equals\(Ljava/lang/Object;\)Z'
            )
            part, n = re.subn(
                pattern,
                lambda m: m.group(1) + m.group(3) + f"    invoke-static {{{m.group(4)}}}, {HELPER}->isCandidate(Ljava/lang/String;)Z",
                part,
            )
            if n != 1:
                raise ValueError(f"Unexpected GIF route structure in at.smali method {name}")
            at_text = at_text[:s] + part + at_text[e:]
    write_text(at_path, at_text)
    print("  + Patched at.smali for animated WebP/GIF candidate detection")

    controller_map = [
        (APKTOOL_OUT / "smali_classes4/com/alensw/ui/c/as.smali", "as", "s", "s", "needsAsUpgrade"),
        (APKTOOL_OUT / "smali/com/alensw/ui/c/dp.smali", "dp", "v", "u", "needsDpUpgrade"),
    ]
    for viewpath, controller, method, flag, helper in controller_map:
        viewtext = read_text(viewpath).replace("\r\n", "\n")
        s, e, part = body_span(viewtext, f".method private {method}()Z")
        if f"{HELPER}->{helper}" not in part:
            part = (
                f".method private {method}()Z\n    .locals 3\n\n"
                f"    iget-boolean v0, p0, Lcom/alensw/ui/c/{controller};->{flag}:Z\n"
                f"    iget-object v1, p0, Lcom/alensw/ui/c/{controller};->f:Lcom/alensw/ui/view/PictureView;\n"
                f"    invoke-virtual {{v1}}, Lcom/alensw/ui/view/PictureView;->getPictureType()I\n"
                f"    move-result v1\n"
                f"    iget-object v2, p0, Lcom/alensw/ui/c/{controller};->f:Lcom/alensw/ui/view/PictureView;\n"
                f"    invoke-virtual {{v2}}, Lcom/alensw/ui/view/PictureView;->getMimeType()Ljava/lang/String;\n"
                f"    move-result-object v2\n"
                f"    invoke-static {{v0, v1, v2}}, {HELPER}->{helper}(ZILjava/lang/String;)Z\n"
                f"    move-result v0\n    return v0\n.end method"
            )
            viewtext = viewtext[:s] + part + viewtext[e:]
            write_text(viewpath, viewtext)
            print(f"  + Patched {controller}.smali for animation upgrade")

    d_path = APKTOOL_OUT / "smali/com/alensw/b/h/d.smali"
    d_text = read_text(d_path).replace("\r\n", "\n")
    s, e, part = body_span(d_text, ".method private a(ILandroid/os/Handler;)V")
    if f"{HELPER}->mimeForHandle" not in part:
        prefix = (
            f"\n    invoke-static {{p1}}, {HELPER}->mimeForHandle(I)Ljava/lang/String;\n"
            f"    move-result-object v0\n"
            f"    iput-object v0, p0, Lcom/alensw/b/h/j;->h:Ljava/lang/String;\n"
        )
        part, n = re.subn(r"(    \.locals \d+\n)", lambda m: m.group(1) + prefix, part, count=1)
        if n != 1:
            raise ValueError("Missing animation initializer locals in d.smali")
        d_text = d_text[:s] + part + d_text[e:]

    s, e, part = body_span(d_text, ".method public static a(Lcom/alensw/b/c/f;Landroid/net/Uri;Landroid/os/Handler;)Lcom/alensw/b/h/d;")
    if '    const-string v2, "load error"' in part:
        pattern = (
            r'(    if-nez v1, :cond_\d+\n\n    :cond_0\n)\s+new-instance v0, Ljava/lang/RuntimeException;\s+'
            r'const-string v2, "load error"\s+'
            r'invoke-direct \{v0, v2\}, Ljava/lang/RuntimeException;-><init>\(Ljava/lang/String;\)V\s+throw v0'
        )
        part, n = re.subn(pattern, lambda m: m.group(1) + "\n    goto :cond_1", part)
        if n != 1:
            raise ValueError("Unexpected zero-handle static fallback in d.smali")
        d_text = d_text[:s] + part + d_text[e:]
    write_text(d_path, d_text)
    print("  + Patched d.smali for animated WebP/GIF handle & static fallback")

    g_path = APKTOOL_OUT / "smali/com/alensw/b/h/g.smali"
    g_text = read_text(g_path).replace("\r\n", "\n")
    s, e, part = body_span(g_text, ".method public d()Ljava/lang/Void;")
    if f"{CLOCK}->beforeFrame" not in part:
        part = part.replace("    .locals 7\n", "    .locals 8\n", 1)
        old = "    if-eqz v0, :cond_0\n\n    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J"
        new = (
            "    if-eqz v0, :cond_0\n\n"
            f"    invoke-static {{p0}}, {CLOCK}->beforeFrame(Ljava/lang/Object;)Z\n"
            "    move-result v1\n    if-eqz v1, :cond_3\n\n"
            "    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J"
        )
        if part.count(old) != 1:
            raise ValueError("Unexpected worker dequeue seam in g.smali")
        part = part.replace(old, new, 1)
        old = (
            "    invoke-static {v1, v4, v5, v6}, Lcom/alensw/b/h/d;->b(Lcom/alensw/b/h/d;III)I\n\n"
            "    move-result v1"
        )
        if part.count(old) != 1:
            raise ValueError("Unexpected worker decode seam in g.smali")
        part = part.replace(old, old + "\n\n    move v7, v1", 1)
        old = "    invoke-static {v0, v1}, Ljava/lang/Math;->max(II)I\n\n    move-result v0"
        if part.count(old) != 1:
            raise ValueError("Unexpected worker wait seam in g.smali")
        part = part.replace(
            old,
            old
            + f"\n\n    invoke-static {{p0, v7, v0}}, {CLOCK}->delayAfterFrame(Ljava/lang/Object;II)I\n"
            + "    move-result v0\n    if-ltz v0, :cond_3",
            1,
        )
        g_text = g_text[:s] + part + g_text[e:]
        write_text(g_path, g_text)
        print("  + Patched g.smali for animation frame scheduling")


def step3_cleanup_duplicates_and_manifest():
    print("=== Step 3: Cleaning Up Duplicate Multidex Classes, AndroidManifest.xml & GalleryActivity ===")

    # 3a. Deduplicate smali classes across smali, smali_classes2, smali_classes3, smali_classes4
    # Keep the first occurrence in dex order (smali -> smali_classes2 -> smali_classes3 -> smali_classes4)
    dex_dirs = ["smali", "smali_classes2", "smali_classes3", "smali_classes4"]
    seen = {}
    removed_dups = 0
    for dex in dex_dirs:
        dex_root = APKTOOL_OUT / dex
        if not dex_root.exists():
            continue
        for smali_file in sorted(dex_root.rglob("*.smali")):
            rel = smali_file.relative_to(dex_root).as_posix()
            if rel in seen:
                smali_file.unlink()
                removed_dups += 1
            else:
                seen[rel] = dex
    print(f"  + Removed {removed_dups} duplicate .smali classes from secondary dex folders")

    # 3b. Remove Umeng Analytics & Device Fingerprinting SDK (b/a/** and com/c/a/**)
    analytic_wrapper = APKTOOL_OUT / "smali/com/alensw/b/f/a.smali"
    clean_analytic = """.class public Lcom/alensw/b/f/a;
.super Ljava/lang/Object;


# direct methods
.method public static a(Landroid/content/Context;I)Ljava/lang/String;
    .locals 1

    const-string v0, "official"

    return-object v0
.end method

.method public static a(Landroid/content/Context;)V
    .locals 0

    return-void
.end method

.method public static a(Landroid/content/Context;Lcom/alensw/b/f/b;)V
    .locals 0

    return-void
.end method

.method public static a(Landroid/content/Context;Lcom/alensw/b/f/b;Ljava/lang/String;)V
    .locals 0

    return-void
.end method

.method public static a(Landroid/content/Context;Lcom/alensw/b/f/b;Ljava/util/Map;)V
    .locals 0

    return-void
.end method

.method public static a(Landroid/content/Context;Lcom/alensw/b/f/b;Ljava/util/Map;I)V
    .locals 0

    return-void
.end method

.method public static a(Ljava/lang/String;)V
    .locals 0

    return-void
.end method

.method public static b(Landroid/content/Context;)V
    .locals 0

    return-void
.end method

.method public static b(Ljava/lang/String;)V
    .locals 0

    return-void
.end method
"""
    write_text(analytic_wrapper, clean_analytic)
    removed_sdk_files = 0
    for dex in dex_dirs:
        for sub in ("b/a", "com/c/a", "com/alensw/updater"):
            target_dir = APKTOOL_OUT / dex / sub
            if target_dir.exists():
                removed_sdk_files += len(list(target_dir.rglob("*.smali")))
                shutil.rmtree(target_dir)
    print(f"  + Removed {removed_sdk_files} Umeng Analytics (b.a.*, com.c.a.*) and self-updater (com.alensw.updater.*) classes")

    # Neutralize MainPreference reference to UpdateView
    mp = APKTOOL_OUT / "smali_classes2/com/alensw/ui/activity/MainPreference.smali"
    mp_text = read_text(mp).replace("\r\n", "\n")
    old_mp_patch = """.method private a__$appendPatch(Landroid/preference/PreferenceScreen;)V
    .locals 4

    invoke-virtual {p1}, Landroid/preference/PreferenceScreen;->getTitle()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-virtual {p0}, Lcom/alensw/ui/activity/MainPreference;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    const v2, 0x7f0a011a

    invoke-virtual {v1, v2}, Landroid/content/res/Resources;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/Object;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    new-instance v1, Landroid/content/Intent;

    invoke-direct {v1}, Landroid/content/Intent;-><init>()V

    invoke-virtual {p0}, Lcom/alensw/ui/activity/MainPreference;->getApplicationContext()Landroid/content/Context;

    move-result-object v2

    const-class v3, Lcom/alensw/updater/UpdateView;

    invoke-virtual {v1, v2, v3}, Landroid/content/Intent;->setClass(Landroid/content/Context;Ljava/lang/Class;)Landroid/content/Intent;

    invoke-virtual {p0, v1}, Lcom/alensw/ui/activity/MainPreference;->startActivity(Landroid/content/Intent;)V

    :cond_0
    return-void
.end method"""
    new_mp_patch = """.method private a__$appendPatch(Landroid/preference/PreferenceScreen;)V
    .locals 0

    return-void
.end method"""
    if new_mp_patch not in mp_text:
        mp_text = replace_once(mp_text, old_mp_patch, new_mp_patch, "MainPreference.a__$appendPatch")
        write_text(mp, mp_text)
        print("  + Neutralized MainPreference.a__$appendPatch updater hook")

    # 3c. Clean up AndroidManifest.xml
    manifest = APKTOOL_OUT / "AndroidManifest.xml"
    m_text = read_text(manifest).replace("\r\n", "\n")

    # Remove invalid/risky permissions that trigger AV grayware heuristics
    for perm_line in (
        '    <uses-permission android:name="android.permission.MANAGE_ALL_FILES"/>\n',
        '    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>\n',
        '    <uses-permission android:minSdkVersion="25" android:name="android.permission.REQUEST_INSTALL_PACKAGES"/>\n',
        '    <uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"/>\n',
    ):
        m_text = m_text.replace(perm_line, "")

    # Remove suspicious hack.quickpic alias and UpdateView activity
    for comp_line in (
        '        <activity-alias android:exported="true" android:name="hack.quickpic.StreamingActivity" android:targetActivity="com.alensw.PicFolder.PlayerActivity"/>\n',
        '        <activity android:configChanges="keyboardHidden|orientation|screenSize" android:exported="true" android:label="@string/update" android:name="com.alensw.updater.UpdateView" android:theme="@style/LaunchScreen"/>\n',
    ):
        m_text = m_text.replace(comp_line, "")

    # Remove android:debuggable="true"
    m_text = m_text.replace(' android:debuggable="true"', "")

    # Remove duplicate MAIN/LAUNCHER intent-filter on GalleryActivity
    dup_intent_filter = """            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
                <category android:name="android.intent.category.LEANBACK_LAUNCHER"/>
            </intent-filter>
"""
    if dup_intent_filter in m_text:
        m_text = m_text.replace(dup_intent_filter, "", 1)

    write_text(manifest, m_text)
    print("  + Cleaned AndroidManifest.xml (removed debuggable=true, duplicate MAIN/LAUNCHER filter, MANAGE_ALL_FILES, READ_PHONE_STATE)")

    # 3c. Clean up GalleryActivity.smali
    ga = APKTOOL_OUT / "smali_classes4/com/alensw/PicFolder/GalleryActivity.smali"
    ga_text = read_text(ga).replace("\r\n", "\n")

    # Fix isStoragePermissionGranted() so it only requests WRITE_EXTERNAL_STORAGE on API 23..29
    old_perm = """.method public isStoragePermissionGranted()Z
    .locals 4

    const/4 v3, 0x1

    const/4 v2, 0x0

    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x17

    if-lt v0, v1, :cond_0

    const-string v0, "android.permission.WRITE_EXTERNAL_STORAGE"

    invoke-virtual {p0, v0}, Lcom/alensw/PicFolder/GalleryActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_1

    :cond_0
    :goto_0
    return v2

    :cond_1
    new-array v0, v3, [Ljava/lang/String;

    const-string v1, "android.permission.WRITE_EXTERNAL_STORAGE"

    aput-object v1, v0, v2

    invoke-static {p0, v0, v3}, Landroidx/core/app/ActivityCompat;->requestPermissions(Landroid/app/Activity;[Ljava/lang/String;I)V

    goto :goto_0
.end method"""

    new_perm = """.method public isStoragePermissionGranted()Z
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
    new-array v0, v3, [Ljava/lang/String;

    const-string v1, "android.permission.WRITE_EXTERNAL_STORAGE"

    aput-object v1, v0, v2

    invoke-static {p0, v0, v3}, Landroidx/core/app/ActivityCompat;->requestPermissions(Landroid/app/Activity;[Ljava/lang/String;I)V

    goto :goto_0
.end method"""

    if new_perm not in ga_text:
        ga_text = replace_once(ga_text, old_perm, new_perm, "GalleryActivity.isStoragePermissionGranted")

    # Make redundant onCreate__$appendPatch2 and onCreate__$appendPatch6 no-ops
    old_p2 = """.method private onCreate__$appendPatch2(Landroid/os/Bundle;)V
    .locals 4
    .annotation build Landroid/annotation/TargetApi;
        value = 0x8
    .end annotation

    const-string v0, "sqlitedatabase"

    const-string v1, "start"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    new-instance v1, Ljava/io/File;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const/4 v3, 0x0

    invoke-virtual {p0, v3}, Lcom/alensw/PicFolder/GalleryActivity;->getExternalFilesDir(Ljava/lang/String;)Ljava/io/File;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    const-string v3, ""

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v1, v2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->exists()Z

    move-result v2

    if-nez v2, :cond_0

    invoke-virtual {v1}, Ljava/io/File;->mkdirs()Z

    :cond_0
    const-string v2, "finished"

    invoke-static {v0, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method"""

    new_p2 = """.method private onCreate__$appendPatch2(Landroid/os/Bundle;)V
    .locals 0

    return-void
.end method"""

    if new_p2 not in ga_text:
        ga_text = replace_once(ga_text, old_p2, new_p2, "GalleryActivity.onCreate__$appendPatch2")

    old_p6 = """.method private onCreate__$appendPatch6(Landroid/os/Bundle;)V
    .locals 2

    const-string v0, "DXP"

    const-string v1, "It works!"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method"""

    new_p6 = """.method private onCreate__$appendPatch6(Landroid/os/Bundle;)V
    .locals 0

    return-void
.end method"""

    if new_p6 not in ga_text:
        ga_text = replace_once(ga_text, old_p6, new_p6, "GalleryActivity.onCreate__$appendPatch6")

    old_p3 = """.method private onCreate__$appendPatch3(Landroid/os/Bundle;)V
    .locals 2

    invoke-virtual {p0}, Lcom/alensw/PicFolder/GalleryActivity;->getCurrentChannel()Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    if-nez v0, :cond_0

    const-string v0, "beta"

    invoke-virtual {p0, v0}, Lcom/alensw/PicFolder/GalleryActivity;->writeUpdateChannelPreference(Ljava/lang/String;)V

    invoke-virtual {p0, v1}, Lcom/alensw/PicFolder/GalleryActivity;->writeUpdatesOnStartup(Z)V

    :cond_0
    invoke-virtual {p0}, Lcom/alensw/PicFolder/GalleryActivity;->getStartupUpdates()Z

    move-result v0

    if-eqz v0, :cond_1

    new-instance v0, Lcom/alensw/updater/UpdaterAssistant;

    invoke-direct {v0, p0, v1}, Lcom/alensw/updater/UpdaterAssistant;-><init>(Landroid/content/Context;Z)V

    invoke-virtual {v0}, Lcom/alensw/updater/UpdaterAssistant;->checkForUpdates()V

    :cond_1
    return-void
.end method"""

    new_p3 = """.method private onCreate__$appendPatch3(Landroid/os/Bundle;)V
    .locals 0

    return-void
.end method"""

    if new_p3 not in ga_text:
        ga_text = replace_once(ga_text, old_p3, new_p3, "GalleryActivity.onCreate__$appendPatch3")

    write_text(ga, ga_text)
    print("  + Cleaned GalleryActivity.smali (API 30+ permission guard, removed redundant appendPatch2/6)")


if __name__ == "__main__":
    step1_patch_smb_and_parcelables()
    step2_port_pure_java_jni_engine()
    step3_cleanup_duplicates_and_manifest()
    print("=== All patches applied successfully! ===")
