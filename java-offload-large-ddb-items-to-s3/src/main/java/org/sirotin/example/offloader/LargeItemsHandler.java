package org.sirotin.example.offloader;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3URI;

import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.UUID;

public class LargeItemsHandler<T> {

    private static final String S3_PATH_PREFIX = "s3://";

    private final AmazonS3 s3Client;
    private final String bucketName;

    public LargeItemsHandler(final AmazonS3 s3Client,
                             final String bucketName) {

        this.s3Client = s3Client;
        this.bucketName = bucketName;
    }

    public void beforeSave(final T item) {

        final ReflectionHelper<T> helper = new ReflectionHelper<>(item);
        final List<Field> candidates = helper.getAndValidateAllFieldsWithAnnotation(LargeItem.class);

        candidates.forEach(field -> {
            final LargeItem annotation = field.getAnnotation(LargeItem.class);

            String value = helper.getStringValue(field);
            if (value.length() > annotation.compressIfLargerThanBytes()) {
                value = GZIPCompression.compress(value);
                helper.setStringValue(field, value);
            }

            if (value.length() > annotation.offloadIfLargerThanBytes()) {
                final String key = String.format("%s%s", annotation.keyPrefix(), UUID.randomUUID());
                s3Client.putObject(bucketName, key, value);

                final String path = String.format("%s%s/%s", S3_PATH_PREFIX, bucketName, key);
                helper.setStringValue(field, Base64.getEncoder().encodeToString(path.getBytes(StandardCharsets.UTF_8)));
            }
        });
    }

    public void afterLoad(final T item) {

        final ReflectionHelper<T> helper = new ReflectionHelper<>(item);
        final List<Field> candidates = helper.getAndValidateAllFieldsWithAnnotation(LargeItem.class);

        for(final Field field : candidates) {

            final String value = helper.getStringValue(field);
            final AmazonS3URI path = tryDecodeS3Path(value);
            if (path == null) {
                helper.setStringValue(field, GZIPCompression.decompress(value));
                continue;
            }

            // For security reasons we will validate the bucket name matches
            if (!path.getBucket().equals(bucketName)) {
                continue;
            }

            final String data = s3Client.getObjectAsString(path.getBucket(), path.getKey());
            helper.setStringValue(field, GZIPCompression.decompress(data));
        }
    }

    private static AmazonS3URI tryDecodeS3Path(final String value) {
        try {
            final String decoded = new String(Base64.getDecoder().decode(value), StandardCharsets.UTF_8);
            return decoded.startsWith(S3_PATH_PREFIX)
                    ? new AmazonS3URI(decoded)
                    : null;

        } catch(final Exception ignored) {
            return null;
        }
    }
}
