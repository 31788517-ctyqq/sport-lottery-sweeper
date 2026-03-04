// Minimal integration test focusing only on utility functions
import { describe, it, expect } from 'vitest';
import {
  calcDeltaPLevel,
  calcDeltaWp,
  calcStabilityTier,
  formatMatchTime,
  normalizeMatches
} from '@/utils/beidanFilterUtils';

describe('Beidan Filter Utilities - Integration Tests', () => {
  describe('1. Pure Functions and Utility Functions', () => {
    it('calcDeltaPLevel correctly calculates strength difference', () => {
      expect(calcDeltaPLevel(100, 70)).toBe(3); // Difference > 25
      expect(calcDeltaPLevel(50, 30)).toBe(2); // Difference 17-25
      expect(calcDeltaPLevel(40, 30)).toBe(1); // Difference 9-16
      expect(calcDeltaPLevel(35, 30)).toBe(0); // Difference -8 to +8
      expect(calcDeltaPLevel(30, 40)).toBe(-1); // Difference -9 to -16
      expect(calcDeltaPLevel(30, 50)).toBe(-2); // Difference -17 to -25
      expect(calcDeltaPLevel(30, 60)).toBe(-3); // Difference < -25
      expect(calcDeltaPLevel('-', '40')).toBe(0);
      expect(calcDeltaPLevel('50', '-')).toBe(0);
    });

    it('calcDeltaWp correctly calculates win pan difference', () => {
      expect(calcDeltaWp(2.0, 0.5)).toBe(4); // 4 - 0 = 4
      expect(calcDeltaWp(1.3, 0.5)).toBe(3); // 3 - 0 = 3
      expect(calcDeltaWp(1.0, 0.5)).toBe(2); // 2 - 0 = 2
      expect(calcDeltaWp(0.7, 0.5)).toBe(1); // 1 - 0 = 1
      expect(calcDeltaWp(0.5, 0.5)).toBe(0); // 0 - 0 = 0
    });

    it('calcStabilityTier correctly calculates stability tier', () => {
      const result1 = calcStabilityTier('一赔70%', '一赔75%');
      expect(result1.tier).toBe('S');
      expect(result1.pLevel).toBe(1);

      const result2 = calcStabilityTier('一赔60%', '一赔55%');
      expect(result2.tier).toBe('A');
      expect(result2.pLevel).toBe(2);

      const result3 = calcStabilityTier('一赔70%', '客队特征');
      expect(result3.tier).toBe('B');
      expect(result3.pLevel).toBe(3);
    });

    it('formatMatchTime correctly formats match time', () => {
      const date = new Date('2023-01-01T12:00:00');
      expect(formatMatchTime(date)).toBe('2023/01/01 12:00:00');
      expect(formatMatchTime('2023-01-01T12:00:00')).toBe('2023/01/01 12:00:00');
      expect(formatMatchTime(null)).toBe('-');
      expect(formatMatchTime(undefined)).toBe('-');
      expect(formatMatchTime('')).toBe('-');
    });

    it('normalizeMatches correctly normalizes match data', () => {
      const mockMatches = [{
        match_id: '123',
        home_team: '主队',
        away_team: '客队',
        power_home: '50',
        power_away: '40',
        win_pan_home: '1.2',
        win_pan_away: '0.8',
        home_feature: '一赔70%',
        away_feature: '一赔40%'
      }];

      const normalized = normalizeMatches(mockMatches);
      expect(normalized).toHaveLength(1);
      expect(normalized[0].power_diff).toBe(1);
      expect(normalized[0].win_pan_diff).toBe(1);
      expect(normalized[0].p_level).toBe(2);
    });
  });
});