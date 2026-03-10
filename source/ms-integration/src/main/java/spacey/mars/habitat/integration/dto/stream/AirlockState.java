package spacey.mars.habitat.integration.dto.stream;

import com.fasterxml.jackson.annotation.JsonProperty;

public enum AirlockState {

	@JsonProperty("IDLE")
	IDLE,

	@JsonProperty("PRESSURIZING")
	PRESSURIZING,

	@JsonProperty("DEPRESSURIZING")
	DEPRESSURIZING

}

