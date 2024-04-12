
# ProcFlow - Point and Click Orchestrator

  

## Overview

This application provides a graphical user interface for orchestrating and validating task chains. It is designed to facilitate easy point-and-click creation, modification, and visualization of task chains with built-in validation functionalities. Future versions will integrate with Microsoft Scheduler to enable automated task scheduling.

  

## Features

-  **Graphical Interface**: Provides a node-based visualization for creating and managing task chains.

-  **Chain Validation**: Ensures that the created chains meet specific logical and functional criteria before execution.

-  **File Management**: Allows users to open, save, and manage project files.

-  **Extensibility**: Designed with scalability in mind, making it easy to add additional features such as integration with external task schedulers.

-  **Custom Console**: Includes a custom command console for direct command execution and feedback.

  

## Installation

  

### Prerequisites

Ensure you have Python 3.x installed on your machine. This application is developed using PyQt5, which requires Python.

  

### Setting Up a Virtual Environment

It's recommended to set up a Python virtual environment for application dependencies:

```
python  -m  venv  venv
source  venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Installing Dependencies
Install the required Python packages using pip:

```
pip install -r requirements.txt
```

## Usage
To run the application, execute the following command from the project's root directory:

```
python src/main.py
```

## File Structure
`src/`: Contains all source files.

-   `ui/`: UI-related modules including the main widget and graphical components.
-   `components/`: Graphical components like nodes and edges.
-   `assets/`: Static files such as icons and images used in the UI.
-   `main.py`: The main entry point of the application.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues to discuss proposed changes or report bugs.

## License
This project is licensed under the MIT License
