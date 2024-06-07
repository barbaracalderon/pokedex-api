import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SwaggerService {
  private apiUrl = 'http://localhost:8000/docs';

  constructor(private http: HttpClient) {}

  getSwagger(): Observable<any> {
    return this.http.get<any>(this.apiUrl);
  }
}
