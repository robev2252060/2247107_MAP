package spacey.mars.habitat.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.Instant;
import java.util.List;

@Getter
@AllArgsConstructor
public class MeasurementEvent {

	private Instant timestamp;

	private String source;

	private String status;

	private List<Measurement> readings;

}
