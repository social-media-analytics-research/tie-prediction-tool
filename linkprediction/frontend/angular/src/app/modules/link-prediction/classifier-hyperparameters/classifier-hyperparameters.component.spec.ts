import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassifierHyperparametersComponent } from './classifier-hyperparameters.component';

describe('ClassifierHyperparametersComponent', () => {
  let component: ClassifierHyperparametersComponent;
  let fixture: ComponentFixture<ClassifierHyperparametersComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ClassifierHyperparametersComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassifierHyperparametersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
