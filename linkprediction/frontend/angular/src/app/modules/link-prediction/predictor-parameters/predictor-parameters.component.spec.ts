import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PredictorParametersComponent } from './predictor-parameters.component';

describe('PredictorParametersComponent', () => {
  let component: PredictorParametersComponent;
  let fixture: ComponentFixture<PredictorParametersComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PredictorParametersComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PredictorParametersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
