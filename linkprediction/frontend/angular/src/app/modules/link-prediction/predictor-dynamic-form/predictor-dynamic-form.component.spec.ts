import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PredictorDynamicFormComponent } from './predictor-dynamic-form.component';

describe('PredictorDynamicFormComponent', () => {
  let component: PredictorDynamicFormComponent;
  let fixture: ComponentFixture<PredictorDynamicFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PredictorDynamicFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PredictorDynamicFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
