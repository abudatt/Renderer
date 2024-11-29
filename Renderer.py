import json
import csv
import os
import streamlit as st

# Helper function to convert frames to timecodes
def frames_to_timecode(frame, fps):
    hours = int(frame // (fps * 3600))
    minutes = int((frame % (fps * 3600)) // (fps * 60))
    seconds = int((frame % (fps * 60)) // fps)
    frames = int(frame % fps)
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

# Function to process the file
def process_file(file):
    try:
        # Output file paths
        base_name = os.path.splitext(file.name)[0]
        html_output = base_name + "_numbered.html"
        csv_output = base_name + "_annotations.csv"

        # Load the input .clqtt file
        data = json.load(file)

        # Extract meta information
        meta = data.get('meta', {})
        fps_str = meta.get('fps', '2400')  # Default to 2400 (24 FPS) if not specified
        fps = int(fps_str) / 100 if fps_str.isdigit() else 24  # Handle scaling (e.g., 2500 = 25 FPS)
        lang = meta.get('lang', 'en')

        # Extract events
        events = data.get('events', {})
        subtitles = []
        for i, (key, event) in enumerate(events.items(), start=1):
            subtitle = {
                "number": i,
                "text": event.get('txt', '').replace("\n", "<br>"),
                "annotations": "<br>".join(
                    ann.get('description', '') for ann in event.get('annotations', {}).values() if isinstance(ann, dict)
                ),
                "start_time": frames_to_timecode(event.get('start', 0), fps),
                "end_time": frames_to_timecode(event.get('end', 0), fps),
                "type_tag": "<span class='type-tag'>FN</span>" if event.get('type') == 'fn' else "",
                "rgn_tag": "<span class='rgn-tag'>Top</span>" if event.get('rgn') == 'top' else ""
            }
            subtitles.append(subtitle)

        # Generate CSV content for annotations
        csv_content = []
        csv_content.append(["Subtitle Number", "Subtitle Text", "Annotation"])
        for subtitle in subtitles:
            if subtitle["annotations"]:
                csv_content.append([subtitle["number"], subtitle["text"], subtitle["annotations"]])

        # Write CSV file for download
        csv_buffer = "\n".join(",".join(map(str, row)) for row in csv_content)

        # Generate HTML content
        html_content = f'''<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Converted</title>
    <style>
        body {{ background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; padding: 20px; }}
        .TimedTextEvent {{
            padding: 10px;
            width: 50rem;
            content-visibility: visible;
            contain: none;
            margin-bottom: 20px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        .TimedTextEvent:hover {{
            background-color: #333333;
        }}
        .timing {{
            display: flex;
            justify-content: flex-start;
            align-items: center;
            font-variant: tabular-nums;
            color: #aaaaaa;
        }}
        .timing .index {{
            margin-right: 1rem;
            font-weight: bold;
            color: white;
        }}
        .timing .timecode {{
            font-size: 0.9em;
        }}
        .subtitle-content {{
            margin-top: 10px;
            font-size: 20px;
            white-space: pre;
        }}
        .tags {{
            margin-top: 10px;
        }}
        .tags span {{
            background: rgb(156, 39, 176);
            padding: 4px 8px;
            border-radius: 5px;
            color: white;
            font-size: 0.9em;
        }}
        .annotations {{
            margin-top: 10px;
            font-style: italic;
        }}
        .annotations .annotation-label {{
            color: rgb(33, 150, 243);
            font-weight: bold;
        }}
        .download-link {{
            display: block;
            margin-bottom: 20px;
            color: #1e90ff;
            text-decoration: none;
            font-weight: bold;
        }}
        .download-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
'''

        for subtitle in subtitles:
            html_content += f'''
<div class="TimedTextEvent">
    <div class="timing">
        <span class="index">{subtitle['number']:04}</span>
        <span class="timecode">{subtitle['start_time']} - {subtitle['end_time']}</span>
    </div>
    <div class="subtitle-content" dir="{'rtl' if lang == 'ar' else 'ltr'}">{subtitle['text']}</div>
    '''
            if subtitle["type_tag"] or subtitle["rgn_tag"]:
                html_content += f'''
    <div class="tags">
        {subtitle["type_tag"]} {subtitle["rgn_tag"]}
    </div>
    '''
            if subtitle["annotations"]:
                html_content += f'''
    <div class="annotations">
        <span class="annotation-label">Annotation:</span> {subtitle["annotations"]}
    </div>
    '''
            html_content += "</div>"

        html_content += '''
</body>
</html>
'''

        return csv_buffer, html_content

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None


# Streamlit App
st.title("CLQTT to HTML & CSV Converter")

file = st.file_uploader("Select .clqtt File", type=["clqtt"])

if file:
    if st.button("Convert File"):
        csv_content, html_content = process_file(file)

        if csv_content and html_content:
            # Provide CSV download
            st.download_button(
                label="Download Annotations CSV",
                data=csv_content,
                file_name="annotations.csv",
                mime="text/csv",
            )

            # Provide HTML download
            st.download_button(
                label="Download HTML",
                data=html_content,
                file_name="converted.html",
                mime="text/html",
            )

            st.success("Conversion complete!")
