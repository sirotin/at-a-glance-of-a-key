package org.sirotin.example.offloader;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface LargeItem {

    long compressIfLargerThanBytes() default 64 * 1024L; // 64K

    long offloadIfLargerThanBytes() default 128 * 1024L; // 128K

    String keyPrefix() default "";
}
