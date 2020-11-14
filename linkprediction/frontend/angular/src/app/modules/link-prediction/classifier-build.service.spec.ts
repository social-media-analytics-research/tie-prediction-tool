import { TestBed } from '@angular/core/testing';

import { ClassifierBuildService } from './classifier-build.service';

describe('ClassifierBuildService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: ClassifierBuildService = TestBed.get(ClassifierBuildService);
    expect(service).toBeTruthy();
  });
});
