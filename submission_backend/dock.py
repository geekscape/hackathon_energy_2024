import json
import os
import docker 
import uuid

def save_docker_submission(client, output_directory, submission_directory):
    if not os.path.exists(output_directory):
        raise ValueError(f"Output directory {output_directory} does not exist")

    if not os.path.exists(submission_directory):
        raise ValueError(f"Submission path {submission_directory} does not exist")


    docker_image_tag = str(uuid.uuid4())
    print('building image')
    result = client.images.build(path=submission_directory, tag=docker_image_tag, quiet=False)
    print(result[0], type(result[0]))
    print(dir(result[0]))

    for item in result[1]:
        print(item)

    print('finished building image')

    container = client.containers.run(
        docker_image_tag, 
        command=f"python evaluate.py --output_file {output_directory}/output.json", 
        volumes={output_directory: {'bind': output_directory, 'mode': 'rw'}},
        detach=True)

    for line in container.logs(stream=True):
        print(line.strip())

    container.stop()
    container.remove()

    client.images.remove(docker_image_tag)

    print('finished running container')

def get_submission_output(client, output_directory, submission_directory):
    save_docker_submission(client, output_directory, submission_directory)

    with open(os.path.join(output_directory, "output.json"), 'r') as f:
        data = json.load(f)

    os.remove(os.path.join(output_directory, "output.json"))

    return data

if __name__ == "__main__":

    print('starting client')
    client = docker.from_env()
    print('finsihed client')

    current_working_directory = os.getcwd()
    output_directory = os.path.join(current_working_directory, "submission_backend", "output")


    output = get_submission_output(client, output_directory, "bot")
    output['main_trial'] = output['trials'][0]
    del output['trials']
    with open('submission_backend/cruft/output.json', 'w') as f:
        json.dump(output, f)