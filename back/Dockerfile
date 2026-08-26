FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /workspace

COPY gradlew gradlew.bat ./
COPY gradle gradle
COPY build.gradle settings.gradle ./
COPY back/build.gradle back/
COPY back/src back/src
COPY db/migration db/migration
RUN chmod +x gradlew && ./gradlew :back:bootJar --no-daemon -x test

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

RUN addgroup -S pivotseoul && adduser -S pivotseoul -G pivotseoul

COPY --from=build /workspace/back/build/libs/*.jar app.jar
RUN chown pivotseoul:pivotseoul app.jar

USER pivotseoul

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "-Dspring.profiles.active=prod", "app.jar"]
