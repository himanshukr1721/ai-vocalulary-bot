import { NextResponse } from "next/server"
import {GoogleGenAI} from '@google/genai';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY as string
if(!GEMINI_API_KEY) {
    throw new Error("GEMINI_API_KEY is not defined in the environment variables.")
}
const ai = new GoogleGenAI({apiKey: GEMINI_API_KEY});
export async function GET() {
  try {
    const prompt = `
      Generate a unique, somewhat advanced English vocabulary word that would be useful for someone to learn.
      Provide the following information in a JSON object:
      {
        "word": "the word",
        "meaning": "concise definition",
        "rephrasedMeaning": "the meaning rephrased in simpler terms for better understanding",
        "synonyms": ["synonym1", "synonym2", "synonym3"],
        "antonyms": ["antonym1", "antonym2"],
        "exampleSentence": "An example sentence using the word correctly."
      }
      
      IMPORTANT: Return ONLY the raw JSON object with no markdown formatting, no code blocks, and no additional text. Make sure to give as unique words as you can so that on refresh none are same.
      Do not wrap the JSON in \`\`\` or any other formatting. Just return the JSON object directly.
    `

    // const { text } = await generateText({
    //   model: google("gemini-1.5-pro"),
    //   prompt,
    // })
    const res = await ai.models.generateContent({
        model: 'gemini-2.0-flash-001',
        contents: prompt,
      });

      if(!res){
        throw new Error("No response from AI model")
      }

      if (res.candidates?.[0]?.content?.parts?.[0]?.text) {
        console.log("AI response:", res.candidates[0].content.parts[0].text);
      } else {
        console.error("AI response is missing expected structure.");
      }

    // Clean the response if it contains markdown code blocks
    let cleanedText: any = res.candidates?.[0]?.content?.parts?.[0]?.text ?? ""

    // Remove markdown code block markers if present
    if (cleanedText.includes("```")) {
      cleanedText = cleanedText.replace(/```json\s*/g, "")
      cleanedText = cleanedText.replace(/```\s*$/g, "")
      cleanedText = cleanedText.replace(/```/g, "")
    }

    // Remove any leading/trailing whitespace
    cleanedText = cleanedText.trim()

    try {
      // Parse the JSON
      const data = JSON.parse(cleanedText)

      // Validate the required fields
      const requiredFields = ["word", "meaning", "rephrasedMeaning", "synonyms", "antonyms", "exampleSentence"]
      for (const field of requiredFields) {
        if (!data[field]) {
          throw new Error(`Missing required field: ${field}`)
        }
      }

      return NextResponse.json(data)
    } catch (parseError) {
      console.error("Error parsing JSON:", parseError)
      console.error("Raw text received:", cleanedText)
      console.error("Cleaned text:", cleanedText)

      return NextResponse.json({ error: "Failed to parse response from AI model" }, { status: 500 })
    }
  } catch (error) {
    console.error("Error generating word:", error)
    return NextResponse.json({ error: "Failed to generate word" }, { status: 500 })
  }
}

