import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PredictorCreatorComponent } from './predictor-creator.component';

describe('PredictorCreatorComponent', () => {
  let component: PredictorCreatorComponent;
  let fixture: ComponentFixture<PredictorCreatorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PredictorCreatorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PredictorCreatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
