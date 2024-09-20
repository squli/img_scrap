# Use an official Ubuntu base image
FROM ubuntu:22.04 AS builder

# Install dependencies
RUN apt-get update && \
    apt-get install -y build-essential cmake gcc-9 g++-9 && \
    apt-get clean

# Copy the project into the container
WORKDIR /usr/src/app

COPY . .

# Create a build directory and set up the project using CMake
RUN cmake -B ./build -S . && cmake --build ./build

# Use lightweight image to run
FROM debian:bookworm-slim

# Get executable
COPY --from=builder /usr/src/app/build/MathClient/MathClient /home/MathClient

# Command to run the executable
CMD ["/home/MathClient"]
