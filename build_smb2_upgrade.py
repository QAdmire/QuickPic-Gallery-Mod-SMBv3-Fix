import os
import shutil
import subprocess
import zipfile

ROOT = r"d:\app-fix"
BUILD_DIR = os.path.join(ROOT, "smb2_build")
SRC_DIR = os.path.join(BUILD_DIR, "src")
CLASSES_DIR = os.path.join(BUILD_DIR, "classes")
DOWNLOADS = os.path.join(ROOT, "tools", "downloads")

JCIFS_JAR = os.path.join(DOWNLOADS, "jcifs-ng-2.1.10.jar")
SLF4J_API_JAR = os.path.join(DOWNLOADS, "slf4j-api-1.7.36.jar")
SLF4J_NOP_JAR = os.path.join(DOWNLOADS, "slf4j-nop-1.7.36.jar")
BCPROV_JAR = os.path.join(DOWNLOADS, "bcprov-jdk15to18-1.76.jar")

JAVAC = os.path.join(ROOT, "tools", "jdk21", "bin", "javac.exe")
JAVA = os.path.join(ROOT, "tools", "jdk21", "bin", "java.exe")
JADX_ALL_JAR = os.path.join(ROOT, "tools", "jadx", "lib", "jadx-1.5.6-all.jar")

if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(CLASSES_DIR, exist_ok=True)

def write_src(rel_path, content):
    full_path = os.path.join(SRC_DIR, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Write compile-time stubs for Android & QuickPic classes referenced by bu.java
write_src("android/content/Context.java", """package android.content;
public class Context {}
""")

write_src("android/content/ContentValues.java", """package android.content;
import java.util.HashMap;
public final class ContentValues {
    public final HashMap<String, Object> map = new HashMap<String, Object>();
    public ContentValues() {}
    public ContentValues(int size) {}
    public void put(String key, String value) { map.put(key, value); }
    public void put(String key, Integer value) { map.put(key, value); }
    public void put(String key, Long value) { map.put(key, value); }
    public String getAsString(String key) { return (String) map.get(key); }
}
""")

write_src("a/d/j.java", """package a.d;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;
public class j extends URLStreamHandler {
    public static final URLStreamHandler a = new j();
    @Override
    protected int getDefaultPort() { return 445; }
    @Override
    protected URLConnection openConnection(URL u) { return null; }
    @Override
    protected void parseURL(URL url, String str, int i, int i2) {
        String host = url.getHost();
        if (str.equals("smb://")) {
            str = "smb:////";
            i2 += 2;
        } else if (!str.startsWith("smb://") && host != null && host.length() == 0) {
            str = "//" + str;
            i2 += 2;
        }
        super.parseURL(url, str, i, i2);
        String path = url.getPath();
        String ref = url.getRef();
        if (ref != null) {
            path = path + '#' + ref;
        }
        int port = url.getPort();
        if (port == -1) {
            port = getDefaultPort();
        }
        setURL(url, "smb", url.getHost(), port, url.getAuthority(), url.getUserInfo(), path, url.getQuery(), null);
    }
}
""")

write_src("com/alensw/b/e/f.java", """package com.alensw.b.e;
public interface f {
    boolean a();
}
""")

write_src("com/alensw/b/e/e.java", """package com.alensw.b.e;
public class e implements f {
    @Override
    public boolean a() { return false; }
}
""")

write_src("com/alensw/b/e/i.java", """package com.alensw.b.e;
import java.io.InputStream;
public class i {
    public long a;
    public long b;
    public String c;
    public String d;
    public InputStream e;
}
""")

write_src("com/alensw/b/e/b.java", """package com.alensw.b.e;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
public class b {
    public static long a(InputStream in, OutputStream out, long len, int bufSize, f cancel) throws IOException {
        return 0L;
    }
    public static void a(Closeable c) {
        if (c != null) {
            try { c.close(); } catch ( Throwable t ) {}
        }
    }
}
""")

write_src("com/alensw/b/f/c.java", """package com.alensw.b.f;
public class c {
    public static char a(String name) { return 'I'; }
    public static String a(String name, char type) { return "image/jpeg"; }
    public static String b(String name) { return "image/jpeg"; }
}
""")

write_src("com/alensw/b/l/b.java", """package com.alensw.b.l;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
public class b {
    public static FileOutputStream e(File f) throws FileNotFoundException {
        return new FileOutputStream(f);
    }
}
""")

write_src("com/alensw/cloud/oauth/aj.java", """package com.alensw.cloud.oauth;
public class aj {
    public String a;
    public String b;
    public String c;
    public long d;
}
""")

write_src("com/alensw/cloud/oauth/a.java", """package com.alensw.cloud.oauth;
public class a {
    public String b;
    public String c;
    public String d;
    public final aj g = new aj();
}
""")

write_src("com/alensw/cloud/a/az.java", """package com.alensw.cloud.a;
import android.content.ContentValues;
import java.util.ArrayList;
public class az extends ArrayList<ContentValues> {
}
""")

write_src("com/alensw/cloud/a/bz.java", """package com.alensw.cloud.a;
public class bz extends Exception {
    public bz(String str) { super(str); }
}
""")

write_src("com/alensw/cloud/a/cb.java", """package com.alensw.cloud.a;
public class cb extends bz {
    public cb(String str) { super(str); }
}
""")

write_src("com/alensw/cloud/a/bv.java", """package com.alensw.cloud.a;
import android.content.ContentValues;
import android.content.Context;
public abstract class bv {
    protected final Context a;
    protected com.alensw.cloud.oauth.aj b;
    public bv(Context context, com.alensw.cloud.oauth.a aVar) {
        this.a = context;
        this.b = aVar != null ? aVar.g : null;
    }
    public static String b(String str) { return str; }
    public static String h() { return ""; }
    public abstract ContentValues a() throws Exception;
    public abstract ContentValues a(String str, String str2, com.alensw.b.e.f fVar) throws Exception;
    public abstract ContentValues a(String str, String str2, com.alensw.b.e.i iVar, com.alensw.b.e.e eVar) throws Exception;
    public ContentValues a(String str, String str2, String str3, com.alensw.b.e.f fVar) throws Exception { return null; }
    protected abstract String a(String str, int i, com.alensw.b.e.f fVar);
    protected abstract String a(String str, com.alensw.b.e.f fVar);
    public abstract void a(String str, ContentValues contentValues, com.alensw.b.e.f fVar) throws Exception;
    public void a(String str, String str2, String str3, com.alensw.b.e.i iVar, com.alensw.b.e.f fVar) throws Exception {}
    public abstract boolean a(String str, az azVar, int i, com.alensw.b.e.f fVar) throws Exception;
    public abstract String b(String str, com.alensw.b.e.f fVar);
    protected void b(String str, String str2, com.alensw.b.e.f fVar) throws Exception {}
    public abstract void c(String str, com.alensw.b.e.f fVar) throws Exception;
    public boolean d_() { return true; }
}
""")

# 2. Write lightweight BouncyCastle-backed jcifs.util.Crypto and jcifs.internal.smb2.Smb2SigningDigest
write_src("jcifs/util/Crypto.java", """package jcifs.util;

import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.Key;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.Provider;
import java.security.spec.AlgorithmParameterSpec;
import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.MacSpi;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.SecretKeySpec;
import jcifs.CIFSUnsupportedCryptoException;
import org.bouncycastle.crypto.digests.MD4Digest;
import org.bouncycastle.crypto.engines.AESEngine;
import org.bouncycastle.crypto.macs.CMac;
import org.bouncycastle.crypto.params.KeyParameter;

public final class Crypto {
    private static Provider provider = null;

    private Crypto() {
    }

    public static MessageDigest getMD4() {
        return new MD4MessageDigest();
    }

    public static MessageDigest getMD5() {
        try {
            return MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new CIFSUnsupportedCryptoException(e);
        }
    }

    public static MessageDigest getSHA512() {
        try {
            return MessageDigest.getInstance("SHA-512");
        } catch (NoSuchAlgorithmException e) {
            throw new CIFSUnsupportedCryptoException(e);
        }
    }

    public static MessageDigest getHMACT64(byte[] key) {
        return new HMACT64(key);
    }

    public static Mac getAESCMAC() {
        return new AESCMACMac();
    }

    public static Cipher getArcfour(byte[] key) {
        try {
            Cipher c = Cipher.getInstance("RC4");
            c.init(1, new SecretKeySpec(key, "RC4"));
            return c;
        } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException e) {
            throw new CIFSUnsupportedCryptoException(e);
        }
    }

    public static Cipher getDES(byte[] key) {
        if (key.length == 7) {
            return getDES(des7to8(key));
        }
        try {
            Cipher c = Cipher.getInstance("DES/ECB/NoPadding");
            c.init(1, new SecretKeySpec(key, "DES"));
            return c;
        } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException e) {
            throw new CIFSUnsupportedCryptoException(e);
        }
    }

    static byte[] des7to8(byte[] key) {
        byte[] key8 = new byte[8];
        key8[0] = (byte) (key[0] & 254);
        key8[1] = (byte) ((key[0] << 7) | ((key[1] & 255) >>> 1));
        key8[2] = (byte) ((key[1] << 6) | ((key[2] & 255) >>> 2));
        key8[3] = (byte) ((key[2] << 5) | ((key[3] & 255) >>> 3));
        key8[4] = (byte) ((key[3] << 4) | ((key[4] & 255) >>> 4));
        key8[5] = (byte) ((key[4] << 3) | ((key[5] & 255) >>> 5));
        key8[6] = (byte) ((key[5] << 2) | ((key[6] & 255) >>> 6));
        key8[7] = (byte) (key[6] << 1);
        for (int i = 0; i < key8.length; i++) {
            key8[i] = (byte) (key8[i] ^ (Integer.bitCount(key8[i] ^ 1) & 1));
        }
        return key8;
    }

    public static Provider getProvider() {
        if (provider != null) {
            return provider;
        }
        provider = new MiniProvider();
        return provider;
    }

    public static void initProvider(Provider customProvider) throws CIFSUnsupportedCryptoException {
        if (provider != null) {
            throw new CIFSUnsupportedCryptoException("Provider can't be re-initialized. Provider has already been initialized with " + provider.getInfo());
        }
        provider = customProvider;
    }

    private static final class MiniProvider extends Provider {
        private static final long serialVersionUID = 1L;
        MiniProvider() {
            super("JCIFSMiniBC", 1.0d, "Lightweight BouncyCastle Provider for JCIFS-NG");
        }
    }

    private static final class MD4MessageDigest extends MessageDigest {
        private final MD4Digest d = new MD4Digest();

        MD4MessageDigest() {
            super("MD4");
        }

        @Override
        protected void engineUpdate(byte input) {
            this.d.update(input);
        }

        @Override
        protected void engineUpdate(byte[] input, int offset, int len) {
            this.d.update(input, offset, len);
        }

        @Override
        protected byte[] engineDigest() {
            byte[] out = new byte[this.d.getDigestSize()];
            this.d.doFinal(out, 0);
            return out;
        }

        @Override
        protected void engineReset() {
            this.d.reset();
        }

        @Override
        protected int engineGetDigestLength() {
            return this.d.getDigestSize();
        }
    }

    private static final class AESCMACMacSpi extends MacSpi {
        private final CMac cmac = new CMac(new AESEngine());

        AESCMACMacSpi() {
        }

        @Override
        protected int engineGetMacLength() {
            return this.cmac.getMacSize();
        }

        @Override
        protected void engineInit(Key key, AlgorithmParameterSpec params) throws InvalidKeyException, InvalidAlgorithmParameterException {
            if (key == null || key.getEncoded() == null) {
                throw new InvalidKeyException("Null key");
            }
            this.cmac.init(new KeyParameter(key.getEncoded()));
        }

        @Override
        protected void engineUpdate(byte input) {
            this.cmac.update(input);
        }

        @Override
        protected void engineUpdate(byte[] input, int offset, int len) {
            this.cmac.update(input, offset, len);
        }

        @Override
        protected byte[] engineDoFinal() {
            byte[] out = new byte[this.cmac.getMacSize()];
            this.cmac.doFinal(out, 0);
            return out;
        }

        @Override
        protected void engineReset() {
            this.cmac.reset();
        }
    }

    private static final class AESCMACMac extends Mac {
        AESCMACMac() {
            super(new AESCMACMacSpi(), Crypto.getProvider(), "AESCMAC");
        }
    }
}
""")

write_src("jcifs/internal/smb2/Smb2SigningDigest.java", """package jcifs.internal.smb2;

import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import jcifs.internal.CommonServerMessageBlock;
import jcifs.internal.SMBSigningDigest;
import jcifs.internal.util.SMBUtil;
import jcifs.util.Crypto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Smb2SigningDigest implements SMBSigningDigest {
    private static final Logger log = LoggerFactory.getLogger(Smb2SigningDigest.class);
    private static final int SIGNATURE_OFFSET = 48;
    private static final int SIGNATURE_LENGTH = 16;
    private final Mac digest;

    public Smb2SigningDigest(byte[] sessionKey, int dialect, byte[] preauthIntegrityHash) throws GeneralSecurityException {
        Mac m;
        byte[] signingKey;
        switch (dialect) {
            case 514:
            case 528:
                m = Mac.getInstance("HmacSHA256");
                signingKey = sessionKey;
                break;
            case 768:
            case 770:
                signingKey = Smb3KeyDerivation.deriveSigningKey(dialect, sessionKey, new byte[0]);
                m = Crypto.getAESCMAC();
                break;
            case 785:
                if (preauthIntegrityHash == null) {
                    throw new IllegalArgumentException("Missing preauthIntegrityHash for SMB 3.1");
                }
                signingKey = Smb3KeyDerivation.deriveSigningKey(dialect, sessionKey, preauthIntegrityHash);
                m = Crypto.getAESCMAC();
                break;
            default:
                throw new IllegalArgumentException("Unknown dialect");
        }
        m.init(new SecretKeySpec(signingKey, "HMAC"));
        this.digest = m;
    }

    @Override
    public synchronized void sign(byte[] data, int offset, int length, CommonServerMessageBlock request, CommonServerMessageBlock response) {
        this.digest.reset();
        int index = offset + SIGNATURE_OFFSET;
        for (int i = 0; i < SIGNATURE_LENGTH; i++) {
            data[index + i] = 0;
        }
        int oldFlags = SMBUtil.readInt4(data, offset + 16);
        int flags = oldFlags | 8;
        SMBUtil.writeInt4(flags, data, offset + 16);
        this.digest.update(data, offset, length);
        byte[] sig = this.digest.doFinal();
        System.arraycopy(sig, 0, data, offset + SIGNATURE_OFFSET, SIGNATURE_LENGTH);
    }

    @Override
    public synchronized boolean verify(byte[] data, int offset, int length, int extraPad, CommonServerMessageBlock msg) {
        this.digest.reset();
        int flags = SMBUtil.readInt4(data, offset + 16);
        if ((flags & 8) == 0) {
            log.error("The server did not sign a message we expected to be signed");
            return true;
        }
        byte[] sig = new byte[SIGNATURE_LENGTH];
        System.arraycopy(data, offset + SIGNATURE_OFFSET, sig, 0, SIGNATURE_LENGTH);
        int index = offset + SIGNATURE_OFFSET;
        for (int i = 0; i < SIGNATURE_LENGTH; i++) {
            data[index + i] = 0;
        }
        this.digest.update(data, offset, length);
        byte[] cmp = new byte[SIGNATURE_LENGTH];
        System.arraycopy(this.digest.doFinal(), 0, cmp, 0, SIGNATURE_LENGTH);
        if (!MessageDigest.isEqual(sig, cmp)) {
            return true;
        }
        return false;
    }
}
""")

# 3. Write com.alensw.cloud.a.bu implementing SMB1/SMB2/SMB3 via jcifs-ng
write_src("com/alensw/cloud/a/bu.java", """package com.alensw.cloud.a;

import a.d.j;
import android.content.ContentValues;
import android.content.Context;
import java.io.Closeable;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.Properties;
import jcifs.CIFSContext;
import jcifs.config.PropertyConfiguration;
import jcifs.context.BaseContext;
import jcifs.smb.NtlmPasswordAuthenticator;
import jcifs.smb.SmbAuthException;
import jcifs.smb.SmbException;
import jcifs.smb.SmbFile;
import jcifs.smb.SmbFileInputStream;
import jcifs.smb.SmbFileOutputStream;

public class bu extends bv {
    private static volatile CIFSContext f;
    private final String c;
    private final String d;
    private final CIFSContext e;

    private static CIFSContext i() {
        if (f == null) {
            synchronized (bu.class) {
                if (f == null) {
                    try {
                        Properties props = new Properties();
                        props.setProperty("jcifs.smb.client.minVersion", "SMB1");
                        props.setProperty("jcifs.smb.client.maxVersion", "SMB311");
                        props.setProperty("jcifs.smb.client.ipcSigningEnforced", "false");
                        props.setProperty("jcifs.smb.client.dfs.disabled", "false");
                        props.setProperty("jcifs.resolveOrder", "DNS,BCAST");
                        props.setProperty("jcifs.smb.client.connTimeout", "10000");
                        props.setProperty("jcifs.smb.client.soTimeout", "35000");
                        props.setProperty("jcifs.smb.client.responseTimeout", "30000");
                        f = new BaseContext(new PropertyConfiguration(props));
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                }
            }
        }
        return f;
    }

    public bu(Context context, com.alensw.cloud.oauth.a aVar) {
        super(context, aVar);
        String str2 = aVar.d;
        int length = str2.length();
        if (length > 0 && str2.charAt(length - 1) != '/') {
            str2 = str2 + '/';
        }
        String path = "/";
        String prefix = "";
        CIFSContext ctx = null;
        try {
            URL url = new URL((URL) null, str2, j.a);
            String origHost = url.getHost();
            String host = origHost;
            int port = url.getPort();
            String urlPath = url.getPath();
            if (urlPath != null && urlPath.length() > 0) {
                path = urlPath;
            }
            int atIdx = aVar.b.lastIndexOf("@" + origHost);
            String rawUser = atIdx >= 0 ? aVar.b.substring(0, atIdx) : aVar.b;
            String domain = null;
            if (host != null) {
                int hostSemi = host.indexOf(59);
                if (hostSemi > 0) {
                    domain = host.substring(0, hostSemi);
                    host = host.substring(hostSemi + 1);
                }
            }
            String userInfo = url.getUserInfo();
            if (userInfo != null && userInfo.length() > 0) {
                int semi = userInfo.indexOf(59);
                if (semi > 0) {
                    domain = userInfo.substring(0, semi);
                }
            }
            if (rawUser != null) {
                int semiIdx = rawUser.indexOf(59);
                int slashIdx = rawUser.indexOf(92);
                int userAtIdx = rawUser.indexOf(64);
                if (semiIdx > 0) {
                    domain = rawUser.substring(0, semiIdx);
                    rawUser = rawUser.substring(semiIdx + 1);
                } else if (slashIdx > 0) {
                    domain = rawUser.substring(0, slashIdx);
                    rawUser = rawUser.substring(slashIdx + 1);
                } else if (userAtIdx > 0) {
                    domain = rawUser.substring(userAtIdx + 1);
                    rawUser = rawUser.substring(0, userAtIdx);
                }
            }
            String pass = (aVar.g != null && aVar.g.b != null) ? aVar.g.b : "";
            NtlmPasswordAuthenticator auth;
            if (rawUser == null || rawUser.length() == 0 || ("guest".equalsIgnoreCase(rawUser) && pass.length() == 0)) {
                auth = new NtlmPasswordAuthenticator(domain, "guest", "", NtlmPasswordAuthenticator.AuthenticationType.GUEST);
            } else {
                auth = new NtlmPasswordAuthenticator(domain, rawUser, pass, NtlmPasswordAuthenticator.AuthenticationType.USER);
            }
            ctx = i().withCredentials(auth);
            if (host != null && host.length() > 0) {
                if (port > 0 && port != 445) {
                    prefix = "smb://" + host + ":" + port;
                } else {
                    prefix = "smb://" + host;
                }
            } else {
                prefix = str2.substring(0, str2.lastIndexOf(path));
            }
        } catch (Exception e) {
            e.printStackTrace();
            int lastIdx = str2.lastIndexOf(path);
            prefix = lastIdx >= 0 ? str2.substring(0, lastIdx) : str2;
        }
        this.c = path;
        this.d = prefix;
        this.e = ctx;
    }

    private SmbFile a(String str) throws MalformedURLException {
        if (str.startsWith("smb://")) {
            return new SmbFile(str, this.e);
        }
        if (str.length() > 0 && str.charAt(0) != '/') {
            return new SmbFile(this.d + '/' + str, this.e);
        }
        return new SmbFile(this.d + str, this.e);
    }

    private SmbFile e(String str) throws MalformedURLException {
        int len = str.length();
        if (len == 0 || str.charAt(len - 1) != '/') {
            str = str + '/';
        }
        return a(str);
    }

    private static boolean a(SmbFile smbFile) {
        return smbFile.getUncPath().length() <= 1;
    }

    private static String a(String str, String str2) {
        int length = str.length();
        if (length > 0 && str.charAt(length - 1) != '/') {
            str = str + '/';
        }
        return str + str2;
    }

    protected char a(String str, SmbFile smbFile, ContentValues contentValues) throws Exception {
        char cA = b("", smbFile, contentValues);
        contentValues.put("document_id", str);
        return cA;
    }

    protected char b(String str, SmbFile smbFile, ContentValues contentValues) throws Exception {
        char cA;
        int i;
        String strA = smbFile.getName();
        boolean isRootOrShare = a(smbFile);
        int iC;
        if (isRootOrShare) {
            iC = (smbFile.getShare() == null) ? 17 : 16;
        } else {
            iC = smbFile.getAttributes();
        }
        boolean z = isRootOrShare || (iC & 16) == 16 || strA.endsWith("/");
        if (z) {
            cA = 'D';
            int length = strA.length();
            if (length > 1 && strA.charAt(length - 1) == '/') {
                strA = strA.substring(0, length - 1);
            }
        } else {
            cA = com.alensw.b.f.c.a(strA);
        }
        if (cA == 0) {
            return (char) 0;
        }
        contentValues.put("document_id", str + strA);
        contentValues.put("_display_name", strA);
        long size = isRootOrShare ? 0L : smbFile.length();
        contentValues.put("_size", Long.valueOf(size));
        long jE = (isRootOrShare ? 0L : smbFile.lastModified()) / 1000L;
        contentValues.put("last_modified", Long.valueOf(jE));
        contentValues.put("datetaken", Long.valueOf(jE));
        contentValues.put("mime_type", z ? "vnd.android.document/directory" : com.alensw.b.f.c.a(strA, cA));
        int i2 = z ? 16 : 1;
        if ((iC & 1) == 0) {
            i = (z ? 10 : 6) | i2;
        } else {
            i = i2;
        }
        contentValues.put("flags", Integer.valueOf(i));
        return cA;
    }

    @Override
    public ContentValues a() {
        ContentValues contentValues = new ContentValues(3);
        contentValues.put("document_id", this.c);
        contentValues.put("mime_type", "vnd.android.document/directory");
        contentValues.put("flags", Integer.valueOf(("/".equals(this.c) ? 0 : 10) | 16));
        return contentValues;
    }

    @Override
    public ContentValues a(String str, String str2, com.alensw.b.e.f fVar) throws Exception {
        ContentValues contentValues = new ContentValues(8);
        try {
            String strA = a(str, str2);
            SmbFile dir = e(strA);
            dir.mkdir();
            a(strA, dir, contentValues);
        } catch (SmbException e) {
            a(e);
        }
        return contentValues;
    }

    @Override
    public ContentValues a(String str, String str2, com.alensw.b.e.i iVar, com.alensw.b.e.e eVar) throws Exception {
        String strA = a(str, str2);
        SmbFile target = null;
        SmbFileOutputStream out = null;
        try {
            target = a(strA);
            if (target.exists() && target.length() > 0) {
                String altPath = a(str, b(str2));
                SmbFile alt = a(altPath);
                if (alt.exists() && alt.length() > 0) {
                    throw new RuntimeException("file already exists");
                }
                strA = altPath;
                target = alt;
            }
            out = new SmbFileOutputStream(target);
            long j = iVar.a;
            long jA = com.alensw.b.e.b.a(iVar.e, out, j, 262144, eVar);
            if (jA < j) {
                throw new RuntimeException("upload wrong bytes: " + jA + "/" + j);
            }
        } catch (SmbException e) {
            a(e);
        } finally {
            com.alensw.b.e.b.a(out);
        }
        if (target != null && iVar.b != 0) {
            try {
                target.setLastModified(iVar.b);
            } catch (Exception ignore) {
            }
        }
        ContentValues contentValues = new ContentValues(8);
        if (target != null) {
            a(strA, target, contentValues);
        }
        return contentValues;
    }

    @Override
    public ContentValues a(String str, String str2, String str3, com.alensw.b.e.f fVar) throws Exception {
        String strSubstring = str.substring(str2.length());
        if (strSubstring.length() > 1 && strSubstring.charAt(0) == '/') {
            strSubstring = strSubstring.substring(1);
        }
        String strA = a(str3, strSubstring);
        SmbFile dst = null;
        try {
            SmbFile src = a(str);
            dst = a(strA);
            if (dst.exists()) {
                throw new RuntimeException("file exists");
            }
            src.renameTo(dst);
        } catch (SmbException e) {
            a(e);
        }
        ContentValues contentValues = new ContentValues(8);
        if (dst != null) {
            a(strA, dst, contentValues);
        }
        return contentValues;
    }

    @Override
    protected String a(String str, int i, com.alensw.b.e.f fVar) {
        return this.d + str;
    }

    @Override
    protected String a(String str, com.alensw.b.e.f fVar) {
        return this.d + str;
    }

    protected void a(SmbException e) throws Exception {
        if (e instanceof SmbAuthException) {
            throw new cb("Error code: " + Integer.toHexString(e.getNtStatus()));
        }
        Throwable cause = e.getCause();
        if (cause instanceof UnknownHostException) {
            throw (UnknownHostException) cause;
        }
        if (cause instanceof SocketTimeoutException) {
            throw (SocketTimeoutException) cause;
        }
        throw e;
    }

    @Override
    public void a(String str, ContentValues contentValues, com.alensw.b.e.f fVar) throws Exception {
        try {
            SmbFile file = a(str);
            if (a(file)) {
                file.connect();
            } else if (!file.exists()) {
                throw new FileNotFoundException(str);
            }
            a(str, file, contentValues);
        } catch (SmbException e) {
            int st = e.getNtStatus();
            if (st == -1073741772 || st == -1073741766 || st == -1073741620) {
                throw new FileNotFoundException(str);
            }
            a(e);
        }
    }

    @Override
    public void a(String str, String str2, String str3, com.alensw.b.e.i iVar, com.alensw.b.e.f fVar) throws Exception {
        String strSubstring;
        int iIndexOf;
        try {
            SmbFile file = a(str);
            SmbFileInputStream in = new SmbFileInputStream(file);
            iVar.c = com.alensw.b.f.c.b(file.getName());
            iVar.d = "";
            iVar.b = file.lastModified();
            iVar.e = in;
            iVar.a = file.length();
            if (str3 == null || !str3.startsWith("bytes=") || (iIndexOf = (strSubstring = str3.substring("bytes=".length())).indexOf(45)) <= 0) {
                return;
            }
            try {
                long j = Long.parseLong(strSubstring.substring(0, iIndexOf));
                iVar.e.skip(j);
                iVar.a -= j;
            } catch (NumberFormatException ignore) {
            }
        } catch (SmbException e) {
            a(e);
        }
    }

    @Override
    public boolean a(String str, az azVar, int i, com.alensw.b.e.f fVar) throws Exception {
        SmbFile[] files = null;
        try {
            files = e(str).listFiles();
        } catch (SmbException e) {
            a(e);
        }
        if (files == null) {
            return true;
        }
        String strA = a(str, "");
        for (int idx = 0; idx < files.length; idx++) {
            SmbFile f = files[idx];
            try {
                String name = f.getName();
                if (a(f)) {
                    if (name.endsWith("$") || name.endsWith("$/")) {
                        continue;
                    }
                } else if ((f.getAttributes() & 2) != 0) {
                    continue;
                }
                ContentValues contentValues = new ContentValues(8);
                if (b(strA, f, contentValues) != 0) {
                    azVar.add(contentValues);
                }
            } catch (SmbException e2) {
                a(e2);
            }
        }
        return true;
    }

    @Override
    public String b(String str, com.alensw.b.e.f fVar) {
        throw new UnsupportedOperationException();
    }

    @Override
    protected void b(String str, String str2, com.alensw.b.e.f fVar) throws Exception {
        Closeable in = null;
        FileOutputStream out = null;
        try {
            SmbFile file = a(str);
            SmbFileInputStream smbIn = new SmbFileInputStream(file);
            in = smbIn;
            out = com.alensw.b.l.b.e(new File(str2));
            com.alensw.b.e.b.a(smbIn, out, file.length(), 262144, fVar);
        } catch (SmbException e) {
            a(e);
        } finally {
            com.alensw.b.e.b.a(in);
            com.alensw.b.e.b.a(out);
        }
    }

    @Override
    public void c(String str, com.alensw.b.e.f fVar) throws Exception {
        try {
            SmbFile file = a(str);
            if (file.isDirectory() && !str.endsWith("/")) {
                file = e(str);
            }
            file.delete();
        } catch (SmbException e) {
            a(e);
        }
    }

    @Override
    public boolean d_() {
        return false;
    }
}
""")

# 4. Write a self-test class to verify Crypto, Smb2SigningDigest (SMB 2.02 - 3.1.1), and bu initialization
write_src("TestSmb2Upgrade.java", """import android.content.ContentValues;
import android.content.Context;
import com.alensw.cloud.a.bu;
import com.alensw.cloud.oauth.a;
import java.security.MessageDigest;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import jcifs.internal.smb2.Smb2SigningDigest;
import jcifs.util.Crypto;

public class TestSmb2Upgrade {
    public static void main(String[] args) throws Exception {
        // 1. Test MD4
        MessageDigest md4 = Crypto.getMD4();
        byte[] digest = md4.digest("test".getBytes("UTF-16LE"));
        if (digest == null || digest.length != 16) {
            throw new AssertionError("MD4 failed");
        }
        // 2. Test AES-CMAC
        Mac cmac = Crypto.getAESCMAC();
        cmac.init(new SecretKeySpec(new byte[16], "HMAC"));
        cmac.update(new byte[64], 0, 64);
        byte[] macOut = cmac.doFinal();
        if (macOut == null || macOut.length != 16) {
            throw new AssertionError("AESCMAC failed");
        }
        // 3. Test Smb2SigningDigest across all SMB2/SMB3 dialects
        int[] dialects = new int[]{0x0202, 0x0210, 0x0300, 0x0302, 0x0311};
        byte[] sessionKey = new byte[16];
        byte[] preauthHash = new byte[64];
        for (int d : dialects) {
            Smb2SigningDigest sd = new Smb2SigningDigest(sessionKey, d, preauthHash);
            byte[] pkt = new byte[128];
            sd.sign(pkt, 0, pkt.length, null, null);
            boolean failed = sd.verify(pkt, 0, pkt.length, 0, null);
            if (failed) {
                throw new AssertionError("Smb2SigningDigest verify failed for dialect 0x" + Integer.toHexString(d));
            }
        }
        // 4. Test bu initialization with guest, user, and domain;user
        a account1 = new a();
        account1.b = "guest@192.168.1.100/";
        account1.d = "smb://192.168.1.100/";
        account1.g.b = "";
        bu driver1 = new bu(new Context(), account1);
        ContentValues cv1 = driver1.a();
        if (!"/".equals(cv1.getAsString("document_id"))) {
            throw new AssertionError("Unexpected root document_id: " + cv1.getAsString("document_id"));
        }

        a account2 = new a();
        account2.b = "WORKGROUP\\\\alice@192.168.1.100/Photos/";
        account2.d = "smb://192.168.1.100/Photos/";
        account2.g.b = "secret123";
        bu driver2 = new bu(new Context(), account2);
        ContentValues cv2 = driver2.a();
        if (!"/Photos/".equals(cv2.getAsString("document_id"))) {
            throw new AssertionError("Unexpected share document_id: " + cv2.getAsString("document_id"));
        }

        System.out.println("ALL SMB2/SMB3 UPGRADE SELF-TESTS PASSED!");
    }
}
""")

print("Compiling Java sources...")
java_files = []
for root, _, files in os.walk(SRC_DIR):
    for f in files:
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))

cp = os.pathsep.join([JCIFS_JAR, SLF4J_API_JAR, SLF4J_NOP_JAR, BCPROV_JAR])
cmd = [JAVAC, "-source", "1.8", "-target", "1.8", "-encoding", "UTF-8", "-cp", cp, "-d", CLASSES_DIR] + java_files
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("JAVAC STDERR:\n", res.stderr)
    raise SystemExit(res.returncode)
print("Compilation succeeded!")

print("Running self-test...")
test_cp = os.pathsep.join([CLASSES_DIR, JCIFS_JAR, SLF4J_API_JAR, SLF4J_NOP_JAR, BCPROV_JAR])
res = subprocess.run([JAVA, "-cp", test_cp, "TestSmb2Upgrade"], capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print("TEST STDERR:\n", res.stderr)
    raise SystemExit(res.returncode)

# 5. Assemble smb2_bundle.jar with tree-shaken jcifs-ng, slf4j, and BouncyCastle
import re

SKIP_PREFIXES = (
    "jcifs/http/",
    "jcifs/https/",
    "jcifs/pac/",
    "jcifs/smb/Kerb5",
    "jcifs/smb/JAASAuthenticator",
    "jcifs/smb/StaticJAASConfiguration",
)

def parse_class_refs(data):
    refs = set()
    for m in re.finditer(rb"L([a-zA-Z0-9_/$]+);", data):
        refs.add(m.group(1).decode("ascii", errors="ignore"))
    for m in re.finditer(rb"(?:org/bouncycastle|jcifs|org/slf4j)/[a-zA-Z0-9_/$]+", data):
        refs.add(m.group(0).decode("ascii", errors="ignore"))
    return refs

bundle_entries = {}

# Load our compiled replacement classes
for root, _, files in os.walk(CLASSES_DIR):
    for f in files:
        if not f.endswith(".class"):
            continue
        full = os.path.join(root, f)
        rel = os.path.relpath(full, CLASSES_DIR).replace(os.sep, "/")
        if rel.startswith(("com/alensw/cloud/a/bu", "jcifs/util/Crypto", "jcifs/internal/smb2/Smb2SigningDigest")):
            with open(full, "rb") as fp:
                bundle_entries[rel] = fp.read()

print(f"Loaded {len(bundle_entries)} custom compiled classes: {sorted(bundle_entries.keys())}")

# Load core jcifs-ng classes
with zipfile.ZipFile(JCIFS_JAR, "r") as zj:
    for n in zj.namelist():
        if not n.endswith(".class"):
            continue
        if n.startswith(SKIP_PREFIXES):
            continue
        if n in bundle_entries:
            continue
        bundle_entries[n] = zj.read(n)

# Load slf4j-api and slf4j-nop classes
for sjar in (SLF4J_API_JAR, SLF4J_NOP_JAR):
    with zipfile.ZipFile(sjar, "r") as zs:
        for n in zs.namelist():
            if n.endswith(".class") and not n.startswith("META-INF/"):
                bundle_entries[n] = zs.read(n)

# Compute transitive closure of org/bouncycastle/* classes needed
bc_needed = set()
for data in bundle_entries.values():
    for ref in parse_class_refs(data):
        if ref.startswith("org/bouncycastle/"):
            bc_needed.add(ref + ".class")

with zipfile.ZipFile(BCPROV_JAR, "r") as zbc:
    bc_available = {n: n for n in zbc.namelist() if n.endswith(".class") and not n.startswith("META-INF/")}
    queue = list(bc_needed)
    bc_visited = set()
    while queue:
        c = queue.pop()
        if c in bc_visited or c not in bc_available:
            continue
        bc_visited.add(c)
        cdata = zbc.read(c)
        bundle_entries[c] = cdata
        for ref in parse_class_refs(cdata):
            if ref.startswith("org/bouncycastle/"):
                rc = ref + ".class"
                if rc not in bc_visited:
                    queue.append(rc)

print(f"Total classes in smb2_bundle.jar: {len(bundle_entries)} (including {len(bc_visited)} BouncyCastle classes)")

BUNDLE_JAR = os.path.join(BUILD_DIR, "smb2_bundle.jar")
with zipfile.ZipFile(BUNDLE_JAR, "w", compression=zipfile.ZIP_DEFLATED) as zb:
    for name in sorted(bundle_entries.keys()):
        zb.writestr(name, bundle_entries[name])

# 6. Convert smb2_bundle.jar to smb2_bundle.dex using dx
BUNDLE_DEX = os.path.join(BUILD_DIR, "smb2_bundle.dex")
print("Running dx to generate smb2_bundle.dex...")
res = subprocess.run([
    JAVA, "-cp", JADX_ALL_JAR, "com.android.dx.command.Main",
    "--dex", f"--output={BUNDLE_DEX}", BUNDLE_JAR
], capture_output=True, text=True)
if res.returncode != 0:
    print("DX STDERR:\n", res.stderr)
    raise SystemExit(res.returncode)
print(f"Generated {BUNDLE_DEX} ({os.path.getsize(BUNDLE_DEX):,} bytes)")

# 7. Disassemble smb2_bundle.dex to smali using baksmali
SMALI_OUT = os.path.join(BUILD_DIR, "smali_out")
print("Running baksmali to disassemble smb2_bundle.dex...")
res = subprocess.run([
    JAVA, "-cp", JADX_ALL_JAR, "com.android.tools.smali.baksmali.Main",
    "d", BUNDLE_DEX, "-o", SMALI_OUT
], capture_output=True, text=True)
if res.returncode != 0:
    print("BAKSMALI STDERR:\n", res.stderr)
    raise SystemExit(res.returncode)

smali_count = sum(len(files) for _, _, files in os.walk(SMALI_OUT))
print(f"Disassembled {smali_count} .smali files into {SMALI_OUT}")

# 8. Install into d:\app-fix\apktool_out
APKTOOL_OUT = os.path.join(ROOT, "apktool_out")

# 8a. Patch a/d/j.smali to remove reference to La/d/bd; and remove all other old jcifs a/{a,b,c,d,e} classes
j_smali_path = os.path.join(APKTOOL_OUT, "smali_classes3", "a", "d", "j.smali")
with open(j_smali_path, "r", encoding="utf-8") as fp:
    j_smali = fp.read()

j_smali = re.sub(
    r"new-instance v0, La/d/bd;\s+invoke-direct \{v0, p1\}, La/d/bd;-><init>\(Ljava/net/URL;\)V",
    "const/4 v0, 0x0",
    j_smali
)

removed_old_jcifs = 0
for sdir in ("smali", "smali_classes2", "smali_classes3"):
    a_root = os.path.join(APKTOOL_OUT, sdir, "a")
    if os.path.exists(a_root):
        for root, _, files in os.walk(a_root):
            for f in files:
                full = os.path.join(root, f)
                if os.path.normcase(full) != os.path.normcase(j_smali_path):
                    os.remove(full)
                    removed_old_jcifs += 1
        # Remove empty directories under a_root
        for root, dirs, files in os.walk(a_root, topdown=False):
            if not os.listdir(root):
                os.rmdir(root)

os.makedirs(os.path.dirname(j_smali_path), exist_ok=True)
with open(j_smali_path, "w", encoding="utf-8", newline="\n") as fp:
    fp.write(j_smali)
print(f"Removed {removed_old_jcifs} old jcifs 1.3 smali files (kept patched a/d/j.smali)")

# 8b. Remove any existing jcifs/ org/slf4j/ org/bouncycastle/ in apktool_out before copying fresh ones
for sdir in ("smali", "smali_classes2", "smali_classes3"):
    for pkg in ("jcifs", "org/slf4j", "org/bouncycastle"):
        p = os.path.join(APKTOOL_OUT, sdir, pkg.replace("/", os.sep))
        if os.path.exists(p):
            shutil.rmtree(p)

# 8c. Copy com/alensw/cloud/a/bu*.smali into smali_classes2 and jcifs/slf4j/bouncycastle into smali_classes3
copied_count = 0
for root, _, files in os.walk(SMALI_OUT):
    for f in files:
        if not f.endswith(".smali"):
            continue
        src_file = os.path.join(root, f)
        rel = os.path.relpath(src_file, SMALI_OUT).replace(os.sep, "/")
        if rel.startswith("com/alensw/cloud/a/bu"):
            dst_file = os.path.join(APKTOOL_OUT, "smali_classes2", rel.replace("/", os.sep))
        else:
            dst_file = os.path.join(APKTOOL_OUT, "smali_classes3", rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)
        copied_count += 1

print(f"Installed {copied_count} new SMBv1/v2/v3 smali files into {APKTOOL_OUT}!")


