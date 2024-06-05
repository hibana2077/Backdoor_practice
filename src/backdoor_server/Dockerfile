FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip

RUN apt install -y iputils-ping net-tools iproute2

EXPOSE 54321

# /bin/bash -c "echo 'Hello, World!' >> /e && tail -f /dev/null"
CMD ["/bin/bash", "-c", "echo 'Hello, World!' >> /e && tail -f /dev/null"]