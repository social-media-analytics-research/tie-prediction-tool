import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PredictionSpinnerComponent } from './prediction-spinner.component';

describe('PredictionSpinnerComponent', () => {
  let component: PredictionSpinnerComponent;
  let fixture: ComponentFixture<PredictionSpinnerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PredictionSpinnerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PredictionSpinnerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
