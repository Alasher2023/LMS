export type Select = {
  label: string
  value: string
}

export type Paper = {
  id?: number
  author?: string
  type?: string
  status?: string
  subject?: string
  grade?: string
  title?: string
  path?: string
  memo?: string
  review_stage?: number
  next_review_date?: string // Using string because JSON transport will serialize datetimes
  last_reviewed_at?: string
  due_date?: string
}
