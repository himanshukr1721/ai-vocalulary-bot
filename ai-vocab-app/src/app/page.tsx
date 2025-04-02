"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { RefreshCw, BookOpen, Lightbulb, AlertCircle } from "lucide-react"

interface WordData {
  word: string
  meaning: string
  rephrasedMeaning: string
  synonyms: string[]
  antonyms: string[]
  exampleSentence: string
}

export default function VocabularyEnhancer() {
  const [wordData, setWordData] = useState<WordData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchNewWord = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch("/api/word")
      const data = await response.json()

      if (!response.ok || data.error) {
        throw new Error(data.error || `API responded with status: ${response.status}`)
      }

      setWordData(data)
    } catch (err:any) {
      console.error("Error fetching word:", err)
      setError(err.message || "Failed to fetch a new word. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNewWord()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        <div className="flex items-center justify-center mb-8">
          <BookOpen className="h-8 w-8 mr-2 text-slate-700" />
          <h1 className="text-3xl font-bold text-slate-800">Vocabulary Enhancer</h1>
        </div>

        {error ? (
          <Card className="w-full">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center justify-center py-6">
                <AlertCircle className="h-8 w-8 text-red-500 mb-4" />
                <div className="text-center text-red-500 mb-4">{error}</div>
                <Button onClick={fetchNewWord}>Try Again</Button>
              </div>
            </CardContent>
          </Card>
        ) : loading ? (
          <Card className="w-full">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-slate-600 mb-4" />
                <p className="text-slate-600">Finding a fascinating word for you...</p>
              </div>
            </CardContent>
          </Card>
        ) : wordData ? (
          <Card className="w-full shadow-lg">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-3xl font-bold text-slate-800">{wordData.word}</CardTitle>
                <Button variant="outline" size="icon" onClick={fetchNewWord} className="h-9 w-9" title="Get a new word">
                  <RefreshCw className="h-4 w-4" />
                  <span className="sr-only">Refresh</span>
                </Button>
              </div>
              <CardDescription className="text-lg text-slate-600 mt-1">{wordData.meaning}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                <div className="flex items-start gap-2">
                  <Lightbulb className="h-5 w-5 text-amber-500 mt-0.5 flex-shrink-0" />
                  <p className="text-slate-700">{wordData.rephrasedMeaning}</p>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-2">EXAMPLE</h3>
                <p className="text-slate-700 italic">"{wordData.exampleSentence}"</p>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-2">SYNONYMS</h3>
                <div className="flex flex-wrap gap-2">
                  {wordData.synonyms.map((synonym, index) => (
                    <Badge key={index} variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-200">
                      {synonym}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-2">ANTONYMS</h3>
                <div className="flex flex-wrap gap-2">
                  {wordData.antonyms.map((antonym, index) => (
                    <Badge key={index} variant="outline" className="text-slate-700">
                      {antonym}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full" onClick={fetchNewWord}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Discover Another Word
              </Button>
            </CardFooter>
          </Card>
        ) : null}

        <p className="text-center text-slate-500 text-sm mt-6">Expand your vocabulary one word at a time</p>
      </div>
    </div>
  )
}

