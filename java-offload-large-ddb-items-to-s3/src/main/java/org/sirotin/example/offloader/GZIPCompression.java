package org.sirotin.example.offloader;

import com.amazonaws.util.IOUtils;
import lombok.SneakyThrows;
import lombok.experimental.UtilityClass;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

@UtilityClass
public class GZIPCompression {

    @SneakyThrows(IOException.class)
    public static String compress(final String str) {

        if (str == null) {
            return null;
        }

        final ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        final GZIPOutputStream gzip = new GZIPOutputStream(bytes);

        gzip.write(str.getBytes(StandardCharsets.UTF_8));
        gzip.flush();
        gzip.close();

        final byte[] compressed = bytes.toByteArray();
        final byte[] encoded = Base64.getEncoder().encode(compressed);
        return new String(encoded, StandardCharsets.UTF_8);
    }

    @SneakyThrows(IOException.class)
    public static String decompress(final String str) {
        if (str == null) {
            return null;
        }

        boolean compressed;
        byte[] decoded = null;
        try {
            decoded = Base64.getDecoder().decode(str);
            compressed = isCompressed(decoded);
        } catch(final Exception ignored) {
            compressed = false;
        }

        if (!compressed) {
            return str;
        }

        ByteArrayInputStream bis = new ByteArrayInputStream(decoded);
        GZIPInputStream gis = new GZIPInputStream(bis);
        byte[] decompressed = IOUtils.toByteArray(gis);
        return new String(decompressed, StandardCharsets.UTF_8);
    }

    public static boolean isCompressed(final byte[] compressed) {
        return (compressed[0] == (byte) (GZIPInputStream.GZIP_MAGIC))
                && (compressed[1] == (byte) (GZIPInputStream.GZIP_MAGIC >> 8));
    }
}

