FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY src/ ${LAMBDA_TASK_ROOT}

WORKDIR /

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD [ "extraction.lambda_handler" ]
