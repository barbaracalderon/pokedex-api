import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';


@Component({
  standalone: true,
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css'],
  imports: [CommonModule]
})
export class DataComponent implements OnInit {
  pokemons: any[] = [];
  loading: boolean = false;
  error: string | null = null;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.fetchPokemons();
  }

  fetchPokemons(): void {
    this.loading = true;
    this.http.get<any>('http://localhost:8000/data').subscribe(
      data => {
        this.pokemons = data.pokemon;
        this.loading = false;
      },
      error => {
        console.error('Error fetching Pokémon data', error);
        this.error = 'Error fetching Pokémon data. Please try again later.';
        this.loading = false;
      }
    );
  }
}