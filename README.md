# CODEBARX - A Custom CODE128 Barcode Generator 📦

A user-friendly application to generate Code 128 barcodes with custom prefixes, designed to meet the needs of a personal project.

## Features ✨

- Generate multiple Code 128 barcodes in ranges 1-5 and 6-9
- Customizable file prefix for organized output
- Modern, intuitive graphical user interface
- Live preview of generated barcodes
- Asynchronous generation for a responsive interface
- Progress tracking for batch generation
- Option to save selected barcodes or all
- Gallery view for easier previewing

## Preview 🖼️

<img src="https://i.imgur.com/8s5FPai.png" alt="CodeBarX Screenshot">

## Requirements ⚙️

- Python 3.6+
- PyQt6
- python-barcode

## Installation 🔧

1. Clone the repository:
    ```bash
    git clone https://github.com/leonardobarrosx/CodeBarX.git
    cd CodeBarX
    ```

2. Install the required packages:

    pip install PyQt6 python-barcode

3. Usage 🚀
    
    Run the application:
        ```
        python codebarx.py
        ```

    Enter the quantity of barcodes needed for each range (1-5 and 6-9)
    
    (Optional) Set a custom file prefix

    Choose a save directory

    Click "Generate Barcodes"

    Use the selection option to save all or only the selected barcodes

## License 📄
This project is open source and available under the MIT License.

## Contributing 🤝
Contributions, issues, and feature requests are welcome. Feel free to check the issues page if you want to contribute.

## Author ✍️
Leonardo Barros

## Acknowledgments 🙏
Thanks to the python-barcode library for barcode generation
PyQt6 for providing the GUI framework
vbnet for the Code 128 barcode generation algorithm

Feel free to adjust any parts as needed! If you need anything else, just let me know. I hope you find this useful!
