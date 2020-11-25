import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AttributeWeightingsComponent } from './attribute-weightings.component';

describe('AttributeWeightingsComponent', () => {
  let component: AttributeWeightingsComponent;
  let fixture: ComponentFixture<AttributeWeightingsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AttributeWeightingsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AttributeWeightingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
