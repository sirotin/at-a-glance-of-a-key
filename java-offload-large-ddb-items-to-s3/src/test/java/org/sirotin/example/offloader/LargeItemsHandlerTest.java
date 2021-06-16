package org.sirotin.example.offloader;

import com.amazonaws.services.s3.AmazonS3;
import lombok.AllArgsConstructor;
import lombok.Data;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.verifyZeroInteractions;
import static org.mockito.Mockito.when;
import static org.mockito.MockitoAnnotations.initMocks;

public class LargeItemsHandlerTest {

    private static final String TEST_BUCKET_NAME = "items";
    private static final String TEST_DATA = "Hello World!";
    private static final String TEST_COMPRESSED_DATA = GZIPCompression.compress(TEST_DATA);
    private static final String TEST_S3_PATH = "s3://"+ TEST_BUCKET_NAME +"/";

    @Mock
    private AmazonS3 mockS3Client;

    @BeforeEach
    public void setup() {
        initMocks(this);
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithNoLargeItems {
        String data;
    }
    @Test
    public void testClassWithNoLargeItems() {
        final LargeItemsHandler<ClassWithNoLargeItems> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithNoLargeItems item = new ClassWithNoLargeItems(TEST_DATA);

        handler.beforeSave(item);
        assertEquals(TEST_DATA, item.getData());

        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        verifyZeroInteractions(mockS3Client);
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithLargeItemBelowThreshold {
        @LargeItem
        String data;
    }
    @Test
    public void testClassWithLargeItemBelowThreshold() {
        final LargeItemsHandler<ClassWithLargeItemBelowThreshold> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithLargeItemBelowThreshold item = new ClassWithLargeItemBelowThreshold(TEST_DATA);

        handler.beforeSave(item);
        assertEquals(TEST_DATA, item.getData());

        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        verifyZeroInteractions(mockS3Client);
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithLargeItemAboveThreshold {
        @LargeItem(offloadIfLargerThanBytes = 0)
        String data;
    }
    @Test
    public void testClassWithLargeItemAboveThreshold() {
        final LargeItemsHandler<ClassWithLargeItemAboveThreshold> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithLargeItemAboveThreshold item = new ClassWithLargeItemAboveThreshold(TEST_DATA);

        when(mockS3Client.getObjectAsString(anyString(), anyString()))
                .thenReturn(TEST_DATA);

        handler.beforeSave(item);
        assertTrue(new String(Base64.getDecoder().decode(item.getData()), StandardCharsets.UTF_8).startsWith(TEST_S3_PATH));

        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        final ArgumentCaptor<String> keyCaptor = ArgumentCaptor.forClass(String.class);
        verify(mockS3Client).putObject(eq(TEST_BUCKET_NAME), keyCaptor.capture(), eq(TEST_DATA));
        assertDoesNotThrow(() -> UUID.fromString(keyCaptor.getValue()));

        verify(mockS3Client).getObjectAsString(eq(TEST_BUCKET_NAME), eq(keyCaptor.getValue()));
        verifyNoMoreInteractions(mockS3Client);
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithLargeItemAboveThresholdAndKeyPrefix {
        @LargeItem(keyPrefix = "folder/", offloadIfLargerThanBytes = 0)
        String data;
    }
    @Test
    public void testClassWithLargeItemAboveThresholdAndKeyPrefix() {
        final LargeItemsHandler<ClassWithLargeItemAboveThresholdAndKeyPrefix> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithLargeItemAboveThresholdAndKeyPrefix item = new ClassWithLargeItemAboveThresholdAndKeyPrefix(TEST_DATA);

        when(mockS3Client.getObjectAsString(anyString(), anyString()))
                .thenReturn(TEST_DATA);

        handler.beforeSave(item);
        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        final ArgumentCaptor<String> keyCaptor = ArgumentCaptor.forClass(String.class);
        verify(mockS3Client).putObject(eq(TEST_BUCKET_NAME), keyCaptor.capture(), eq(TEST_DATA));
        assertTrue(keyCaptor.getValue().startsWith("folder/"));
        assertDoesNotThrow(() -> UUID.fromString(keyCaptor.getValue().substring("folder/".length())));
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithLargeItemWithCompressionNoOffloading {
        @LargeItem(compressIfLargerThanBytes = 0)
        String data;
    }
    @Test
    public void testClassWithLargeItemWithCompressionNoOffloading() {
        final LargeItemsHandler<ClassWithLargeItemWithCompressionNoOffloading> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithLargeItemWithCompressionNoOffloading item = new ClassWithLargeItemWithCompressionNoOffloading(TEST_DATA);

        handler.beforeSave(item);
        assertNotEquals(TEST_DATA, item.getData());
        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        verifyZeroInteractions(mockS3Client);
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithLargeItemWithCompressionAndOffloading {
        @LargeItem(compressIfLargerThanBytes = 0, offloadIfLargerThanBytes = 0)
        String data;
    }
    @Test
    public void testClassWithLargeItemWithCompressionAndOffloading() {
        final LargeItemsHandler<ClassWithLargeItemWithCompressionAndOffloading> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithLargeItemWithCompressionAndOffloading item = new ClassWithLargeItemWithCompressionAndOffloading(TEST_DATA);

        when(mockS3Client.getObjectAsString(anyString(), anyString()))
                .thenReturn(TEST_COMPRESSED_DATA);

        handler.beforeSave(item);
        assertTrue(new String(Base64.getDecoder().decode(item.getData()), StandardCharsets.UTF_8).startsWith(TEST_S3_PATH));

        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        verify(mockS3Client).putObject(eq(TEST_BUCKET_NAME), anyString(), eq(TEST_COMPRESSED_DATA));
    }

    @Data
    @AllArgsConstructor
    private static class ClassWithLargeItemWithOffloadingNoCompression {
        @LargeItem(offloadIfLargerThanBytes = 0)
        String data;
    }
    @Test
    public void testClassWithLargeItemWithOffloadingNoCompression() {
        final LargeItemsHandler<ClassWithLargeItemWithOffloadingNoCompression> handler = new LargeItemsHandler<>(mockS3Client, TEST_BUCKET_NAME);
        final ClassWithLargeItemWithOffloadingNoCompression item = new ClassWithLargeItemWithOffloadingNoCompression(TEST_DATA);

        when(mockS3Client.getObjectAsString(anyString(), anyString()))
                .thenReturn(TEST_DATA);

        handler.beforeSave(item);
        assertTrue(new String(Base64.getDecoder().decode(item.getData()), StandardCharsets.UTF_8).startsWith(TEST_S3_PATH));

        handler.afterLoad(item);
        assertEquals(TEST_DATA, item.getData());

        verify(mockS3Client).putObject(eq(TEST_BUCKET_NAME), anyString(), eq(TEST_DATA));
    }
}
