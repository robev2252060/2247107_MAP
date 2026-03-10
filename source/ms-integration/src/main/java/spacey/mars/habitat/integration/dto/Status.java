package spacey.mars.habitat.integration.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public enum Status {

	@JsonProperty("ok")
	OK,

	@JsonProperty("warning")
	WARNING

}
