import whisper
from pydub import AudioSegment
import re
from presidio_analyzer import AnalyzerEngine

def transcribe_audio(input_file):
    model = whisper.load_model("base")
    result = model.transcribe(input_file, word_timestamps=True)
    return result

def create_word(word_info, is_redact=False):
    return {
        'word': word_info['word'],
        'start': word_info['start'],
        'end': word_info['end'],
        'redact': is_redact,
    }

def redact_transcript(segments):
    redacted_segments = []
    for segment in segments:
        words = segment['words']
        bad_words = analyze(''.join([w['word'] for w in words]))
        start=0
        pii_idx=0
        for index,word_info in enumerate(words):
            start+=len(words[index-1]['word']) if index>0 else 0
            end = start+len(words[index]['word'])
            pii_start = bad_words[pii_idx].start
            pii_end = bad_words[pii_idx].end
            if pii_start<=end and end<pii_end:
                redacted_segments.append(create_word(word_info, is_redact=True))
            elif pii_end<=end and start<pii_end:
                pii_idx+=1
                redacted_segments.append(create_word(word_info, is_redact=True))
            else:
                redacted_segments.append(create_word(word_info))

    return redacted_segments

def is_pii(word):
    return word['redact']

def analyze(trnascript):
    analyzer = AnalyzerEngine()

    print(f"getting piis for: {trnascript}")
    results = analyzer.analyze(text=trnascript,
                            entities=["PERSON", "LOCATION", "ORGANIZATION", "DATE_TIME"],
                            language='en')
    return results

def redact_words(input_file, output_file):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)
    
    # Transcribe the audio and get timestamps
    transcription = transcribe_audio(input_file)
    
    if not transcription or 'segments' not in transcription:
        print("Transcription failed or no segments found.")
        return

    word_timestamps = redact_transcript(transcription['segments'])
    redacted_audio = audio

    print("Transcription and Word-level Timestamps:")
    for word_info in word_timestamps:
        start_time_ms = int(word_info['start'] * 1000)
        end_time_ms = int(word_info['end'] * 1000)
        
        if is_pii(word_info):
            # Create silence for the duration of the word
            silence = AudioSegment.silent(duration=end_time_ms - start_time_ms)
            redacted_audio = redacted_audio[:start_time_ms] + silence + redacted_audio[end_time_ms:]
    
    # Export the redacted audio to a new file
    redacted_audio.export(output_file, format="wav")

if __name__ == "__main__":
    input_file = "input.wav"
    output_file = "input_redacted.wav"

    redact_words(input_file, output_file)