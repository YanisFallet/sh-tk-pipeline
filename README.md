# SH-TK Pipeline

## Overview

The SH-TK Pipeline is a comprehensive tool designed to automate the process of downloading, processing, and uploading videos from Instagram to TikTok. This project leverages various Python libraries and APIs to streamline the workflow, ensuring efficient and reliable video management.

## Features

- **Download Videos**: Automatically download videos from Instagram based on specified criteria.
- **Video Processing**: Process downloaded videos to meet TikTok's requirements, including format conversion and metadata handling.
- **Upload to TikTok**: Upload processed videos to TikTok using automated scripts.
- **Concurrency**: Utilize concurrent processing to handle multiple videos simultaneously, improving performance and efficiency.
- **Error Handling**: Robust error handling to manage issues like corrupted videos and API challenges.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/sh-tk-pipeline.git
    cd sh-tk-pipeline
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Ensure you have FFmpeg installed:
    ```bash
    brew install ffmpeg
    ```

## Usage

1. **Configure the Project**:
    - Update the configuration files with your Instagram and TikTok credentials.
    - Set the necessary parameters in the configuration files.

2. **Run the Pipeline**:
    - Execute the main script to start the pipeline:
        ```bash
        python core/main.py
        ```

3. **Monitor Progress**:
    - The pipeline will log its progress and any errors encountered. Check the logs for detailed information.

## Project Structure

- [core](http://_vscodecontentref_/0): Contains the main scripts and modules for the pipeline.
- [data](http://_vscodecontentref_/1): Database files and data management scripts.
- `insta_download/`: Modules for downloading videos from Instagram.
- `create_content/`: Modules for processing and uploading videos to TikTok.
- [README.md](http://_vscodecontentref_/2): Project documentation.

## Contributing

We welcome contributions to the SH-TK Pipeline project. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch to your fork.
4. Open a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- Thanks to the developers of the `instagrapi` and `moviepy` libraries for their excellent tools.
- Special thanks to the open-source community for their contributions and support.

## Contact

For any questions or issues, please open an issue on GitHub or contact the project maintainer at your.email@example.com.
