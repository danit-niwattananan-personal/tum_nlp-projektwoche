import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import yt_dlp

def get_data_path(data_dir: str = "data") -> Path:
    """Get the absolute path to the data directory."""
    return Path(__file__).parent.parent.parent / data_dir

def sample_movies_by_genre(
    df: pd.DataFrame,
    genres: List[str],
    movies_per_genre: int = 3,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Sample movies from each genre.
    
    Args:
        df: DataFrame containing movie data
        genres: List of genres to sample from
        movies_per_genre: Number of movies to sample per genre
        random_state: Random seed for reproducibility
    
    Returns:
        DataFrame containing sampled movies
    """
    sampled_movies = []
    for genre in genres:
        genre_movies = df[df[genre] == 1]
        sampled = genre_movies.sample(n=movies_per_genre, random_state=random_state)
        sampled_movies.append(sampled)
    
    return pd.concat(sampled_movies).drop_duplicates()

def create_id_mapping(metadata: Dict) -> Dict[str, str]:
    """
    Create a mapping between movie IDs and database IDs.
    
    Args:
        metadata: Dictionary containing movie metadata
    
    Returns:
        Dictionary mapping movie IDs to database IDs
    """
    id_mapping = {}
    for db_id in metadata['trailers12k'].keys():
        movie_id = metadata['trailers12k'][db_id]['imdb']['id']
        id_mapping[movie_id] = db_id
    return id_mapping

def get_youtube_ids(
    movie_ids: List[str],
    id_mapping: Dict[str, str],
    metadata: Dict
) -> Tuple[Dict[str, str], List[str]]:
    """
    Get YouTube IDs for the given movie IDs.
    
    Args:
        movie_ids: List of movie IDs
        id_mapping: Dictionary mapping movie IDs to database IDs
        metadata: Dictionary containing movie metadata
    
    Returns:
        Tuple of (youtube_id to movie_id mapping, list of failed movie IDs)
    """
    youtube_movie_ids_map = {}
    failed_movies = []
    
    for movie_id in movie_ids:
        if movie_id in id_mapping:
            db_id = id_mapping[movie_id]
            youtube_id = metadata['trailers12k'][db_id]['youtube']['trailers'][0]['id']
            youtube_movie_ids_map[youtube_id] = movie_id
        else:
            failed_movies.append(movie_id)
    
    return youtube_movie_ids_map, failed_movies

def download_trailer(
    youtube_id: str,
    output_path: Path,
    ydl_opts: Optional[Dict] = None
) -> bool:
    """
    Download a trailer from YouTube.
    
    Args:
        youtube_id: YouTube video ID
        output_path: Path to save the video
        ydl_opts: Optional yt-dlp options
    
    Returns:
        True if download was successful, False otherwise
    """
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Simplified format selection
        'outtmpl': str(output_path / '%(id)s.%(ext)s'),
        'quiet': False,
        'verbose': True,
        # 'listformats': True,
        # 'no_warnings': True,
        # Add client configuration to avoid SABR streaming issues
        # 'client_version': '2.20240215.01.00',
        # 'client_name': 'android',
        'client': 'mweb',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f'https://www.youtube.com/watch?v={youtube_id}'])
            return True
        except Exception as e:
            print(f"Could not download video {youtube_id}: {str(e)}")
            return False

def download_trailers(
    youtube_ids: List[str],
    output_path: Path
) -> Tuple[int, List[str]]:
    """
    Download multiple trailers.
    
    Args:
        youtube_ids: List of YouTube video IDs
        output_path: Path to save the videos
    
    Returns:
        Tuple of (number of successful downloads, list of failed video IDs)
    """
    successful_downloads = 0
    failed_downloads = []
    
    for youtube_id in youtube_ids:
        if download_trailer(youtube_id, output_path):
            successful_downloads += 1
        else:
            failed_downloads.append(youtube_id)
    
    return successful_downloads, failed_downloads

def main(
    data_dir: str = "data",
    movies_per_genre: int = 3,
    random_state: int = 42
) -> None:
    """
    Main function to sample and download movie trailers.
    
    Args:
        data_dir: Directory containing data files
        movies_per_genre: Number of movies to sample per genre
        random_state: Random seed for reproducibility
    """
    # Setup paths
    data_path = get_data_path(data_dir)
    trailers_path = data_path / "trailers"
    trailers_path.mkdir(exist_ok=True)
    
    # Define genres
    genres = ['action', 'adventure', 'comedy', 'crime', 'drama', 
              'fantasy', 'horror', 'romance', 'sci-fi', 'thriller']
    
    # Read and sample movies
    df = pd.read_csv(data_path / 'mtgc.csv')
    final_sample = sample_movies_by_genre(df, genres, movies_per_genre, random_state)
    # final_sample.to_csv(data_path / 'sampled_trailers.csv', index=False)
    
    # Print sampling statistics
    print(f"Total number of movies in sample: {len(final_sample)}")
    print("\nNumber of movies per genre:")
    for genre in genres:
        print(f"\n{genre}: {sum(final_sample[genre])}")
        print("Movie IDs:", final_sample[final_sample[genre] == 1]['mid'].tolist())
    
    # Process movie IDs
    movie_ids = [id.replace('tt', '') for id in final_sample['mid'].tolist()]
    
    # Load metadata and create mappings
    with open(data_path / 'metadata.json', 'r') as f:
        metadata = json.load(f)
    
    id_mapping = create_id_mapping(metadata)
    youtube_movie_ids_map, failed_movies = get_youtube_ids(movie_ids, id_mapping, metadata)
    
    if failed_movies:
        print("\nFailed to find YouTube IDs for movies:", failed_movies)
    
    # Download trailers
    successful_downloads, failed_downloads = download_trailers(
        list(youtube_movie_ids_map.keys()),
        trailers_path
    )
    
    # Print final statistics
    print(f'\nSuccessfully downloaded {successful_downloads} trailers')
    if failed_downloads:
        print(f'Failed to download {len(failed_downloads)} trailers:')
        for youtube_id in failed_downloads:
            print(f"- {youtube_id} (Movie ID: {youtube_movie_ids_map[youtube_id]})")
    
    space_used = sum(os.path.getsize(f) for f in trailers_path.iterdir())
    print(f'Space used: {space_used / (1024 * 1024):.2f} MB')

if __name__ == "__main__":
    main()