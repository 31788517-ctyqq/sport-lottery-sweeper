import { describe, it, expect } from 'vitest'
import {
  unique,
  chunk,
  groupBy,
  sum,
  sortBy
} from '../../src/utils/array.js'

describe('array utils release smoke', () => {
  it('deduplicates primitive values', () => {
    expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3])
  })

  it('chunks items by requested size', () => {
    expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]])
  })

  it('groups data and calculates totals', () => {
    const rows = [
      { league: 'A', points: 3 },
      { league: 'A', points: 1 },
      { league: 'B', points: 2 }
    ]
    const grouped = groupBy(rows, (item) => item.league)

    expect(Object.keys(grouped)).toEqual(['A', 'B'])
    expect(sum(grouped.A, (item) => item.points)).toBe(4)
  })

  it('sorts in descending order', () => {
    const rows = [{ score: 1 }, { score: 3 }, { score: 2 }]
    const sorted = sortBy(rows, 'score', 'desc')
    expect(sorted.map((row) => row.score)).toEqual([3, 2, 1])
  })
})
