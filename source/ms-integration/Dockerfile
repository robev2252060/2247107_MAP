FROM maven:3.9.9-eclipse-temurin-21 AS mvn-package
WORKDIR /app

COPY pom.xml ./
COPY src ./src

RUN mvn -B -DskipTests clean package

FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=mvn-package /app/target/integration-0.0.1-SNAPSHOT.jar /app/app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "/app/app.jar"]

