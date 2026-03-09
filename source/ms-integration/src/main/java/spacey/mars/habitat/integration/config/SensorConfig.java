package spacey.mars.habitat.integration.config;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class SensorConfig {

	private String id;
	private SensorType type;

}
