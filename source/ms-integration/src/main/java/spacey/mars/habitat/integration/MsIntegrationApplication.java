package spacey.mars.habitat.integration;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import spacey.mars.habitat.integration.config.*;
import spacey.mars.habitat.integration.service.SensorPollingService;
import spacey.mars.habitat.integration.service.SensorConsumerService;

@SpringBootApplication
public class MsIntegrationApplication {

	public static void main(String[] args) {
		SpringApplication.run(MsIntegrationApplication.class, args);
	}

}

@Component
class SensorBootstrap {

	private final SensorRegistry sensorRegistry;
	private final SensorPollingService pollingService;
	private final SensorConsumerService sensorConsumerService;

	SensorBootstrap(
		SensorRegistry sensorRegistry,
		SensorPollingService pollingService,
		SensorConsumerService sensorConsumerService
	) {
		this.sensorRegistry = sensorRegistry;
		this.pollingService = pollingService;
		this.sensorConsumerService = sensorConsumerService;
	}

	@EventListener(ContextRefreshedEvent.class)
	void initialize() {
		// Register REST sensors with prefix
		sensorRegistry.registerRest(new SensorConfig("greenhouse_temperature", SensorType.SCALAR_V1));
		sensorRegistry.registerRest(new SensorConfig("entrance_humidity", SensorType.SCALAR_V1));
		sensorRegistry.registerRest(new SensorConfig("co2_hall", SensorType.SCALAR_V1));
		sensorRegistry.registerRest(new SensorConfig("hydroponic_ph", SensorType.CHEMISTRY_V1));
		sensorRegistry.registerRest(new SensorConfig("water_tank_level", SensorType.LEVEL_V1));
		sensorRegistry.registerRest(new SensorConfig("corridor_pressure", SensorType.SCALAR_V1));
		sensorRegistry.registerRest(new SensorConfig("air_quality_pm25", SensorType.PARTICULATE_V1));
		sensorRegistry.registerRest(new SensorConfig("air_quality_voc", SensorType.CHEMISTRY_V1));

		// Register SSE/Stream topics
		sensorRegistry.registerStream(new SensorConfig("solar_array", SensorType.POWER_V1));
		sensorRegistry.registerStream(new SensorConfig("radiation", SensorType.ENVIRONMENT_V1));
		sensorRegistry.registerStream(new SensorConfig("life_support", SensorType.ENVIRONMENT_V1));
		sensorRegistry.registerStream(new SensorConfig("thermal_loop", SensorType.THERMAL_LOOP_V1));
		sensorRegistry.registerStream(new SensorConfig("power_bus", SensorType.POWER_V1));
		sensorRegistry.registerStream(new SensorConfig("power_consumption", SensorType.POWER_V1));
		sensorRegistry.registerStream(new SensorConfig("airlock", SensorType.AIRLOCK_V1));

		// Start polling and consuming
		pollingService.startAll();
		sensorConsumerService.startAll();
	}
}
