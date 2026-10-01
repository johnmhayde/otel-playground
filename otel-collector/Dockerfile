FROM golang:1.26 AS build
WORKDIR /src
RUN go install go.opentelemetry.io/collector/cmd/builder@v0.161.0
COPY builder-config.yaml .
RUN CGO_ENABLED=0 builder --config=builder-config.yaml

FROM gcr.io/distroless/static-debian12
COPY --from=build /src/build/otelcol-custom /otelcol-custom
ENTRYPOINT ["/otelcol-custom"]
