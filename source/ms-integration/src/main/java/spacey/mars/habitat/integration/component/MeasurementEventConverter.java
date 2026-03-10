package spacey.mars.habitat.integration.component;

import org.springframework.stereotype.Component;
import spacey.mars.habitat.integration.dto.Measurement;
import spacey.mars.habitat.integration.dto.MeasurementEvent;
import spacey.mars.habitat.integration.dto.Status;
import spacey.mars.habitat.integration.dto.polling.ChemistryV1;
import spacey.mars.habitat.integration.dto.polling.LevelV1;
import spacey.mars.habitat.integration.dto.polling.ParticulateV1;
import spacey.mars.habitat.integration.dto.polling.ScalarV1;
import spacey.mars.habitat.integration.dto.stream.AirlockV1;
import spacey.mars.habitat.integration.dto.stream.EnvironmentV1;
import spacey.mars.habitat.integration.dto.stream.PowerV1;
import spacey.mars.habitat.integration.dto.stream.ThermalLoopV1;

import java.util.List;

@Component
public class MeasurementEventConverter {

	public MeasurementEvent convert(Object payload) {

		if(payload instanceof ScalarV1 scalarV1)
			return fromScalar(scalarV1);

		if(payload instanceof ChemistryV1 chemistryV1)
			return fromChemistry(chemistryV1);

		if(payload instanceof LevelV1 levelV1)
			return fromLevel(levelV1);

		if(payload instanceof ParticulateV1 particulateV1)
			return fromParticulate(particulateV1);

		if(payload instanceof PowerV1 powerV1)
			return fromPower(powerV1);

		if(payload instanceof EnvironmentV1 environmentV1)
			return fromEnvironment(environmentV1);

		if(payload instanceof ThermalLoopV1 thermalLoopV1)
			return fromThermalLoop(thermalLoopV1);

		if(payload instanceof AirlockV1 airlockV1)
			return fromAirlock(airlockV1);

		throw new IllegalArgumentException("Unsupported payload type: " + payload.getClass().getName());
	}

	public MeasurementEvent fromScalar(ScalarV1 payload) {
		return new MeasurementEvent(
			payload.getCapturedAt(),
			payload.getSensorId(),
			toStatusString(payload.getStatus()),
			List.of(new Measurement(payload.getMetric(), payload.getValue(), payload.getUnit()))
		);
	}

	public MeasurementEvent fromChemistry(ChemistryV1 payload) {
		return new MeasurementEvent(
			payload.getCapturedAt(),
			payload.getSensorId(),
			toStatusString(payload.getStatus()),
			payload.getMeasurements()
		);
	}

	public MeasurementEvent fromLevel(LevelV1 payload) {
		return new MeasurementEvent(
			payload.getCapturedAt(),
			payload.getSensorId(),
			toStatusString(payload.getStatus()),
			List.of(
				new Measurement("level_pct", payload.getLevelPct()),
				new Measurement("level_liters", payload.getLevelLiters())
			)
		);
	}

	public MeasurementEvent fromParticulate(ParticulateV1 payload) {
		return new MeasurementEvent(
			payload.getCapturedAt(),
			payload.getSensorId(),
			toStatusString(payload.getStatus()),
			List.of(
				new Measurement("pm1_ug_m3", payload.getPm1UgM3()),
				new Measurement("pm25_ug_m3", payload.getPm25UgM3()),
				new Measurement("pm10_ug_m3", payload.getPm10UgM3())
			)
		);
	}

	public MeasurementEvent fromPower(PowerV1 payload) {
		return new MeasurementEvent(
			payload.getEventTime(),
			payload.getTopic(),
			null,
			List.of(
				new Measurement("subsystem", payload.getSubsystem()),
				new Measurement("power_kw", payload.getPowerKw()),
				new Measurement("voltage_v", payload.getVoltageV()),
				new Measurement("current_a", payload.getCurrentA()),
				new Measurement("cumulative_kwh", payload.getCumulativeKwh())
			)
		);
	}

	public MeasurementEvent fromEnvironment(EnvironmentV1 payload) {
		return new MeasurementEvent(
			payload.getEventTime(),
			payload.getTopic(),
			toStatusString(payload.getStatus()),
			payload.getMeasurements()
		);
	}

	public MeasurementEvent fromThermalLoop(ThermalLoopV1 payload) {
		return new MeasurementEvent(
			payload.getEventTime(),
			payload.getTopic(),
			toStatusString(payload.getStatus()),
			List.of(
				new Measurement("loop", payload.getLoop()),
				new Measurement("temperature_c", payload.getTemperatureC()),
				new Measurement("flow_l_min", payload.getFlowLMin())
			)
		);
	}

	public MeasurementEvent fromAirlock(AirlockV1 payload) {
		return new MeasurementEvent(
			payload.getEventTime(),
			payload.getTopic(),
			null,
			List.of(
				new Measurement("airlock_id", payload.getAirlockId()),
				new Measurement("cycles_per_hour", payload.getCyclesPerHour()),
				new Measurement("last_state", payload.getLastState().name())
			)
		);
	}

	private String toStatusString(Status status) {
		return status != null
			? status.name().toLowerCase()
			: null;
	}

}

