import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassifierDetailsComponent } from './classifier-details.component';

describe('ClassifierDetailsComponent', () => {
  let component: ClassifierDetailsComponent;
  let fixture: ComponentFixture<ClassifierDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ClassifierDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassifierDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
