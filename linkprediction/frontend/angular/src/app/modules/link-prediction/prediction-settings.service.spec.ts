import { TestBed } from '@angular/core/testing';

import { PredictionSettingsService } from './prediction-settings.service';

describe('LinkPredictionService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: PredictionSettingsService = TestBed.get(PredictionSettingsService);
    expect(service).toBeTruthy();
  });
});
