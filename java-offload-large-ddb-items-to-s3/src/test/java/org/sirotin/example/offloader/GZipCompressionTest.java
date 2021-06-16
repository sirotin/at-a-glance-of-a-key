package org.sirotin.example.offloader;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class GZipCompressionTest {

    @Test
    public void testRepeatingString_100_100K() {
        testRepeatingStringCompression(100, 100);
    }

    @Test
    public void testRepeatingString_100_400K() {
        testRepeatingStringCompression(100, 400);
    }

    @Test
    public void testRepeatingString_1000_100K() {
        testRepeatingStringCompression(1000, 100);
    }

    @Test
    public void testRepeatingString_1000_400K() {
        testRepeatingStringCompression(1000, 400);
    }

    private void testRepeatingStringCompression(final int itemsInDictionary, final int KB) {
        final List<String> dictionary = new ArrayList<>();
        for(int i = 0; i < itemsInDictionary; ++i) {
            dictionary.add(RandomStringUtils.randomAlphanumeric(16));
        }

        final StringBuilder sb = new StringBuilder(KB * 1024);
        final Random rand = new Random();
        for (int i = 0; i < KB * 1024 / 16; ++i) {
            sb.append(dictionary.get(rand.nextInt(itemsInDictionary)));
        }

        final String data = sb.toString();
        System.out.printf("Data set is build with %d items in dictionary%n", itemsInDictionary);
        compressDecompress(data);
    }

    @Test
    public void testRandomStringCompression_100K() {
        testRandomStringCompression(100);
    }
    @Test
    public void testRandomStringCompression_400K() {
        testRandomStringCompression(400);
    }

    private void testRandomStringCompression(final int KB) {
        final String data = RandomStringUtils.randomAlphanumeric(KB * 1024);
        compressDecompress(data);
    }

    private void compressDecompress(final String data) {
        final String compressed = GZIPCompression.compress(data);
        System.out.printf("Data size: %d : Compressed size: %d%n", data.length(), compressed.length());

        final String decompressed = GZIPCompression.decompress(compressed);
        assertEquals(data, decompressed);
    }
}
