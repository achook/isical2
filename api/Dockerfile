FROM golang:1.17-alpine AS build

RUN apk add build-base

WORKDIR /api
COPY ./* .
RUN go get ./...
RUN go build -o api *.go

FROM alpine:latest AS production
WORKDIR /api
COPY --from=build /api/api .

ENV DB_PATH "/data/db.sqlite"

CMD ["./api"]
EXPOSE 8080