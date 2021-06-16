package org.sirotin.example.offloader;

import java.lang.annotation.Annotation;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class ReflectionHelper<T> {

    private final T item;

    public ReflectionHelper(final T item) {
        this.item = item;
    }

    // We cannot use reflection getFields() as it will return only the public fields, hence we should iterate over
    // the whole hierarchy and get all the fields annotated with the provided annotation type
    public List<Field> getAndValidateAllFieldsWithAnnotation(final Class<? extends Annotation> type) {

        final List<Field> fields = getAllFieldsWithAnnotation(type);

        // Validate that all the identified fields have a getter and a setter as we expect
        fields.forEach(field -> {
            final String value = getStringValue(field);
            setStringValue(field, value);
        });

        return fields;
    }

    private List<Field> getAllFieldsWithAnnotation(final Class<? extends Annotation> type) {

        final List<Field> fields = new ArrayList<>();

        Class<?> clazz = item.getClass();
        do {
            fields.addAll(
                    Arrays.stream(clazz.getDeclaredFields())
                            .filter(field -> field.isAnnotationPresent(type))
                            .collect(Collectors.toList())
            );
            clazz = clazz.getSuperclass();

        } while (clazz != null);

        return Collections.unmodifiableList(fields);
    }

    // The assumption is that there is a getter
    public String getStringValue(final Field field) {
        try {
            final String methodName = buildMethodName("get", field.getName());

            final Object o = item.getClass().getMethod(methodName).invoke(item);
            return o == null
                    ? null
                    : (String) o;

        } catch(final Exception e) {
            final String message = String.format("Failed getting value of %s", field.getName());
            throw new RuntimeException(message, e);
        }
    }

    // The assumption is that there is a setter
    public void setStringValue(final Field field, final String value) {
        try {
            final String methodName = buildMethodName("set", field.getName());
            item.getClass().getMethod(methodName, String.class).invoke(item, value);

        } catch(final Exception e) {
            final String message = String.format("Failed setting value of %s", field.getName());
            throw new RuntimeException(message, e);
        }
    }

    private static String buildMethodName(final String prefix, final String fieldName) {
        return String.format("%s%c%s",
                prefix,
                fieldName.toUpperCase().charAt(0),
                fieldName.substring(1));
    }
}
