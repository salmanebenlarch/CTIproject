export type NewsCategory = 'all' | 'security' | 'ai' | 'cloud' | 'privacy' | 'devtools' | 'startups'

export interface NewsStory {
  id: number
  title: string
  by?: string | null
  url?: string | null
  score: number
  descendants: number
  time: number
  hn_url: string
  categories: NewsCategory[]
}
