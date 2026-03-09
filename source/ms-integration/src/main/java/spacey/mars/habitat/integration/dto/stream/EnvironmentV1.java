package spacey.mars.habitat.integration.dto.stream;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import spacey.mars.habitat.integration.dto.Measurement;
import spacey.mars.habitat.integration.dto.Status;

import java.time.Instant;
import java.util.List;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class EnvironmentV1 {

	private String topic;

	@JsonProperty("event_time")
	private Instant eventTime;

	private Source source;

	private List<Measurement> measurements;

	private Status status;

	@Getter
	@NoArgsConstructor
	@AllArgsConstructor
	public static class Source {
		private String system;
		private String segment;
	}

}
