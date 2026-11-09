# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
import shutil

APKTOOL_OUT = Path(r"d:\app-fix\apktool_out")

def patch_common_folder():
    p = APKTOOL_OUT / r"smali\com\alensw\bean\CommonFolder.smali"
    text = p.read_text(encoding="utf-8").replace("\r\n", "\n")

    old_a = """.method public a(Landroid/content/ContentResolver;Landroid/database/ContentObserver;)V
    .locals 2

    invoke-virtual {p0}, Lcom/alensw/bean/CommonFolder;->i()Landroid/net/Uri;

    move-result-object v0

    const/4 v1, 0x0

    invoke-virtual {p1, v0, v1, p2}, Landroid/content/ContentResolver;->registerContentObserver(Landroid/net/Uri;ZLandroid/database/ContentObserver;)V

    return-void
.end method"""

    new_a = """.method public a(Landroid/content/ContentResolver;Landroid/database/ContentObserver;)V
    .locals 3

    :try_start_0
    invoke-virtual {p0}, Lcom/alensw/bean/CommonFolder;->i()Landroid/net/Uri;

    move-result-object v0

    if-eqz v0, :cond_0

    const-string v1, "content"

    invoke-virtual {v0}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    const/4 v1, 0x0

    invoke-virtual {p1, v0, v1, p2}, Landroid/content/ContentResolver;->registerContentObserver(Landroid/net/Uri;ZLandroid/database/ContentObserver;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_0
    :goto_0
    return-void

    :catch_0
    move-exception v0

    goto :goto_0
.end method"""

    old_b = """.method public b(Landroid/content/ContentResolver;Landroid/database/ContentObserver;)V
    .locals 0

    invoke-virtual {p1, p2}, Landroid/content/ContentResolver;->unregisterContentObserver(Landroid/database/ContentObserver;)V

    return-void
.end method"""

    new_b = """.method public b(Landroid/content/ContentResolver;Landroid/database/ContentObserver;)V
    .locals 1

    :try_start_0
    invoke-virtual {p1, p2}, Landroid/content/ContentResolver;->unregisterContentObserver(Landroid/database/ContentObserver;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :goto_0
    return-void

    :catch_0
    move-exception v0

    goto :goto_0
.end method"""

    assert old_a in text or new_a in text, "CommonFolder.a target not found"
    assert old_b in text or new_b in text, "CommonFolder.b target not found"
    text = text.replace(old_a, new_a).replace(old_b, new_b)
    p.write_text(text, encoding="utf-8", newline="\n")
    print("Patched CommonFolder.smali")


def patch_dd():
    p = APKTOOL_OUT / r"smali\com\alensw\ui\c\dd.smali"
    text = p.read_text(encoding="utf-8").replace("\r\n", "\n")

    old_pat = """    const/4 v0, 0x2

    invoke-static {p2, v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;I)Ljava/util/regex/Pattern;

    move-result-object v0

    iput-object v0, p0, Lcom/alensw/ui/c/dd;->d:Ljava/util/regex/Pattern;"""

    new_pat = """    const/4 v0, 0x2

    :try_start_pat
    invoke-static {p2, v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;I)Ljava/util/regex/Pattern;

    move-result-object v0
    :try_end_pat
    .catch Ljava/lang/Throwable; {:try_start_pat .. :try_end_pat} :catch_pat

    :goto_pat
    iput-object v0, p0, Lcom/alensw/ui/c/dd;->d:Ljava/util/regex/Pattern;"""

    old_end = """    iput-object v2, p0, Lcom/alensw/ui/c/dd;->f:Lcom/alensw/bean/CommonFolder;

    goto :goto_0
.end method"""

    new_end = """    iput-object v2, p0, Lcom/alensw/ui/c/dd;->f:Lcom/alensw/bean/CommonFolder;

    goto :goto_0

    :catch_pat
    move-exception v0

    invoke-static {p2}, Ljava/util/regex/Pattern;->quote(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x2

    invoke-static {v0, v1}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;I)Ljava/util/regex/Pattern;

    move-result-object v0

    goto :goto_pat
.end method"""

    if old_pat in text:
        assert old_end in text, "dd.smali end target not found"
        text = text.replace(old_pat, new_pat, 1).replace(old_end, new_end, 1)
        p.write_text(text, encoding="utf-8", newline="\n")
        print("Patched dd.smali")
    else:
        assert new_pat in text, "dd.smali pattern block not found"
        print("dd.smali already patched")


def patch_aw_and_bd():
    for fname in ("aw.smali", "bd.smali"):
        p = APKTOOL_OUT / rf"smali_classes4\com\alensw\ui\c\{fname}"
        text = p.read_text(encoding="utf-8").replace("\r\n", "\n")
        old_call = """    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2}, Landroid/content/ContentResolver;->notifyChange(Landroid/net/Uri;Landroid/database/ContentObserver;)V"""

        new_call = """    :try_start_nc
    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2}, Landroid/content/ContentResolver;->notifyChange(Landroid/net/Uri;Landroid/database/ContentObserver;)V
    :try_end_nc
    .catch Ljava/lang/Throwable; {:try_start_nc .. :try_end_nc} :catch_nc

    :goto_nc"""

        if old_call in text:
            text = text.replace(old_call, new_call, 1)
            text = text.replace(
                "    return-void\n.end method",
                "    return-void\n\n    :catch_nc\n    move-exception v0\n\n    goto :goto_nc\n.end method",
                1,
            )
            p.write_text(text, encoding="utf-8", newline="\n")
            print(f"Patched {fname}")
        else:
            assert new_call in text, f"{fname} target not found"
            print(f"{fname} already patched")


if __name__ == "__main__":
    patch_common_folder()
    patch_dd()
    patch_aw_and_bd()
