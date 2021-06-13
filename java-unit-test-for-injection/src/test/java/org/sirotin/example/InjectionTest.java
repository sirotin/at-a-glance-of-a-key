package org.sirotin.example;

import com.amazonaws.regions.Regions;
import com.google.inject.Inject;
import com.google.inject.Injector;
import com.google.inject.internal.util.ImmutableSet;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;
import org.reflections.util.ClasspathHelper;
import org.reflections.util.ConfigurationBuilder;
import org.sirotin.example.guice.MyModule;

import java.lang.reflect.Constructor;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static com.google.inject.Guice.createInjector;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class InjectionTest {

    private final static Set<String> PACKAGES = ImmutableSet.of(
            "org.sirotin.example"
    );

    private final static Regions TEST_REGION = Regions.US_EAST_1;
    private static Injector injector;

    @BeforeAll
    public static void setup() {
        injector = createInjector(new MyModule(TEST_REGION));
    }

    @ParameterizedTest
    @MethodSource("getClassesToInject")
    public void testTableSizePeriodicReporterInjection(final Class<?> type) {

        final Object obj = assertDoesNotThrow(() -> injector.getInstance(type));
        assertNotNull(obj);
    }

    private static Stream<Arguments> getClassesToInject() {

        final List<Arguments> result = new ArrayList<>();
        PACKAGES.forEach(packageName -> result.addAll(getClassesForPackage(packageName)));
        return result.stream();
    }

    private static List<Arguments> getClassesForPackage(final String packageName) {

        final Reflections reflections = new Reflections(
                new ConfigurationBuilder()
                        .setUrls(ClasspathHelper.forPackage(packageName))
                        .setScanners(new SubTypesScanner(false))
        );

        final Set<Class<?>> types = reflections.getSubTypesOf(Object.class);
        return types.stream()
                .filter(InjectionTest::isAnnotatedWithInject)
                .map(Arguments::of)
                .collect(Collectors.toList());
    }

    private static boolean isAnnotatedWithInject(final Class<?> clazz) {

        for(final Constructor<?> constructor : clazz.getConstructors()) {
            if (constructor.isAnnotationPresent(Inject.class)) {
                return true;
            }
        }
        return false;
    }
}
