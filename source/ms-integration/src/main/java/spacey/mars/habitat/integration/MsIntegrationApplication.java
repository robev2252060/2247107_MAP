package spacey.mars.habitat.integration;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import spacey.mars.habitat.integration.config.SensorConfig;
import spacey.mars.habitat.integration.config.SensorRegistry;
import spacey.mars.habitat.integration.config.SensorType;
import spacey.mars.habitat.integration.service.SensorPollingService;

@SpringBootApplication
public class MsIntegrationApplication {

	public static void main(String[] args) {
		SpringApplication.run(MsIntegrationApplication.class, args);
	}

}

@Component
class SensorBootstrap {

	private final SensorRegistry registry;
	private final SensorPollingService pollingService;

	SensorBootstrap(SensorRegistry registry, SensorPollingService pollingService) {
		this.registry = registry;
		this.pollingService = pollingService;
	}

	@EventListener(ContextRefreshedEvent.class)
	void initialize() {
		registry.register(new SensorConfig("greenhouse_temperature", SensorType.SCALAR_V1));
		registry.register(new SensorConfig("entrance_humidity", SensorType.SCALAR_V1));
		registry.register(new SensorConfig("co2_hall", SensorType.SCALAR_V1));
		registry.register(new SensorConfig("hydroponic_ph", SensorType.CHEMISTRY_V1));
		registry.register(new SensorConfig("water_tank_level", SensorType.LEVEL_V1));
		registry.register(new SensorConfig("corridor_pressure", SensorType.SCALAR_V1));
		registry.register(new SensorConfig("air_quality_pm25", SensorType.PARTICULATE_V1));
		registry.register(new SensorConfig("air_quality_voc", SensorType.CHEMISTRY_V1));

		pollingService.startAll();
	}
}
