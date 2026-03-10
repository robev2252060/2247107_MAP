package spacey.mars.habitat.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class Measurement {

	private String metric;

	private Object value;

	private String unit;

	public Measurement(String metric, Object value) {
		this.metric = metric;
		this.value = value;
	}

}
