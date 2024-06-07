import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css']
})
export class DataComponent implements OnInit {
  pokemons: any[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.fetchPokemons();
  }

  fetchPokemons(): void {
    this.http.get<any[]>('http://localhost:8000/data').subscribe(
      data => {
        this.pokemons = data;
      },
      error => {
        console.error('Error fetching Pokémon data', error);
      }
    );
  }
}
