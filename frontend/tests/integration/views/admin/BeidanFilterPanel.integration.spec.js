// Integration tests for BeidanFilterPanel business logic
import { describe, it, expect, vi } from 'vitest';
import {
  calcDeltaPLevel,
  calcDeltaWp,
  calcStabilityTier,
  formatMatchTime,
  normalizeMatches
} from '@/utils/beidanFilterUtils';

describe('BeidanFilterPanel Integration Tests', () => {
  it('should correctly process the full data flow', () => {
    // Simulate processing a match with all calculations
    const rawMatch = {
      match_id: '12345',
      home_team: '主队',
      away_team: '客队',
      power_home: '55',
      power_away: '40',
      win_pan_home: '1.3',
      win_pan_away: '0.7',
      home_feature: '一赔70%',
      away_feature: '一赔45%'
    };

    // Calculate individual metrics
    const powerDiff = calcDeltaPLevel(rawMatch.power_home, rawMatch.power_away);
    const winPanDiff = calcDeltaWp(rawMatch.win_pan_home, rawMatch.win_pan_away);
    const stabilityResult = calcStabilityTier(rawMatch.home_feature, rawMatch.away_feature);

    // Verify calculations
    expect(powerDiff).toBe(1); // 55-40=15 -> +1 (difference between 9-16)
    expect(winPanDiff).toBe(2); // 1.3->score 3, 0.7->score 1, diff=3-1=2
    expect(stabilityResult.tier).toBe('A'); // 70+45=115 -> A
    expect(stabilityResult.pLevel).toBe(2);

    // Normalize the match
    const normalized = normalizeMatches([rawMatch]);
    expect(normalized[0].power_diff).toBe(powerDiff);
    expect(normalized[0].win_pan_diff).toBe(winPanDiff);
    expect(normalized[0].stability).toBe(stabilityResult.tier);
    expect(normalized[0].p_level).toBe(stabilityResult.pLevel);
  });

  it('should handle edge cases in data processing', () => {
    // Test with invalid data
    const rawMatch = {
      match_id: '12345',
      power_home: '-',
      power_away: '-',
      win_pan_home: '-',
      win_pan_away: '-',
      home_feature: '',
      away_feature: ''
    };

    const powerDiff = calcDeltaPLevel(rawMatch.power_home, rawMatch.power_away);
    const winPanDiff = calcDeltaWp(rawMatch.win_pan_home, rawMatch.win_pan_away);
    const stabilityResult = calcStabilityTier(rawMatch.home_feature, rawMatch.away_feature);

    expect(powerDiff).toBe(0);
    expect(winPanDiff).toBe(0);
    expect(stabilityResult.tier).toBe('E');
    expect(stabilityResult.pLevel).toBe(7);

    const normalized = normalizeMatches([rawMatch]);
    expect(normalized[0].power_diff).toBe(0);
    expect(normalized[0].win_pan_diff).toBe(0);
    expect(normalized[0].stability).toBe('E');
    expect(normalized[0].p_level).toBe(7);
  });

  it('should format dates correctly in various scenarios', () => {
    const date = new Date('2023-06-15T19:30:00');
    const formatted = formatMatchTime(date);
    expect(formatted).toBe('2023/06/15 19:30:00');

    const isoString = '2023-06-15T19:30:00';
    const formattedIso = formatMatchTime(isoString);
    expect(formattedIso).toBe('2023/06/15 19:30:00');
  });
});