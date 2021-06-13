package org.sirotin.example;

import com.amazonaws.regions.Regions;
import com.google.inject.Injector;
import org.sirotin.example.guice.MyModule;
import lombok.SneakyThrows;
import org.sirotin.example.utils.TableSizePeriodicReporter;

import static com.google.inject.Guice.createInjector;

public class Main {

    @SneakyThrows(InterruptedException.class)
    public static void main(final String[] args) {

        final Regions region = getRegionOrDie(args);
        final Injector injector = createInjector(
                new MyModule(region)
        );

        final TableSizePeriodicReporter tableSizeReporter = injector.getInstance(TableSizePeriodicReporter.class);
        tableSizeReporter.start();

        // Oops, looks like we have a dead-lock that keeps the program running.
        Thread.currentThread().join();
    }

    private static Regions getRegionOrDie(final String[] args) {

        try {
            return Regions.fromName(args[0]);

        } catch(final Exception e) {
            System.err.printf("Could not parse region from arguments: %s%n", args[0]);
            System.exit(1);

            // Make our compiler happy.
            return null;
        }
    }
}